import csv
import xml.sax
import pytz
import iso8601

from collections import Counter
from tqdm import tqdm
from dateutil import parser, tz

from django.conf import settings
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import Point, GEOSGeometry
from django.utils import timezone

from .models import Ingest, Tree, PropertySet


def parse_point(point_string):
    if not point_string:
        return None

    try:
        (x, y) = (float(n) for n in point_string.split(','))
    except ValueError:
        raise ParseError('Invalid geometry string supplied for parameter {0}'.format(self.point_param))

    p = Point(x, y, srid=4326)
    p.transform(25833)

    return p


def get_timestamp(filename):

    class GMLHandler(xml.sax.ContentHandler):

        timestamp = None

        def startElement(self, name, attrs):
            if name == "wfs:FeatureCollection":
                self.timestamp = attrs['timeStamp']

    handler = GMLHandler()
    parser = xml.sax.make_parser()
    parser.setContentHandler(handler)
    parser.parse(filename)

    timestamp = iso8601.parse_date(handler.timestamp, default_timezone=None)
    return pytz.timezone(settings.TIME_ZONE).localize(timestamp)


def ingest_trees_from_file(dataset, filename):

    try:
        column_names = _parse_column_names_csv()
    except AttributeError:
        column_names = {}

    # parse the file using a sax parser to get the timestamp
    downloaded_at = get_timestamp(filename)

    # parse the file (probably gml) with the gdal DataSource class
    data_source = DataSource(filename)

    # create an object in the ingest table
    ingest = Ingest.objects.create(
        dataset=dataset,
        filename=filename,
        downloaded_at=downloaded_at,
        ingested_at=timezone.now()
    )

    # prepare counter
    counter = Counter()

    # loop over features in the data source (i.e. the trees)
    for feature in tqdm(data_source[0]):
        # parse the point from the point in the feature
        point = GEOSGeometry(str(feature.geom), srid=25833)

        # try to get the tree with the same location or create a new one
        try:
            tree = Tree.objects.get(location=point)
        except Tree.DoesNotExist:
            tree = Tree(location=point)

        # create attributes dict for this tree
        ingest_properties = {}
        for key in feature.fields:
            if key in column_names:
                column_name = column_names[key]
            else:
                column_name = key

            ingest_properties[column_name] = feature[key].value

        if tree.properties:

            update = True
            for propertyset in tree.propertysets.all():
                if ingest_properties == propertyset.properties:
                    update = False
                    break

            if update:
                # the properties have changed, we will add the new properties to the history
                propertyset = PropertySet.objects.create(
                    tree=tree,
                    ingest=ingest,
                    properties=ingest_properties
                )

                # now we need to update the tree for the current_propertyset
                tree.current_propertyset = propertyset
                tree.save()

                counter['updated'] += 1
            else:
                # nothing has changed, we will skip this tree
                counter['skipped'] += 1

        else:
            # this tree has no properties, it must be a new tree
            # first we need to save the tree
            tree.save()

            # then we store the properties
            propertyset = PropertySet.objects.create(
                tree=tree,
                ingest=ingest,
                properties=ingest_properties
            )

            # now we need to update the tree for the current_propertyset
            tree.current_propertyset = propertyset
            tree.save()

            counter['new'] += 1

    return counter


def _parse_column_names_csv():
    column_names = {}
    with open(settings.COLUMN_NAMES_CSV, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        for row in reader:
            if row:
                for column_name in row[1].split(';'):
                    if column_name:
                        column_names[column_name] = row[0]

    return column_names
