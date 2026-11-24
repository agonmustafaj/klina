"""Initial PostGIS schema for CityOS

Revision ID: 001
Revises:
Create Date: 2026-03-24

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from geoalchemy2 import Geometry

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "municipal_boundary",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("name_local", sa.String(128)),
        sa.Column("osm_relation_id", sa.BigInteger(), unique=True),
        sa.Column("source", sa.String(256), nullable=False),
        sa.Column("source_url", sa.Text()),
        sa.Column("area_km2", sa.Float()),
        sa.Column("geom", Geometry("MULTIPOLYGON", srid=4326), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_municipal_boundary_geom", "municipal_boundary", ["geom"], postgresql_using="gist")

    op.create_table(
        "settlements",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("osm_id", sa.BigInteger(), index=True),
        sa.Column("name", sa.String(256), nullable=False, index=True),
        sa.Column("name_local", sa.String(256)),
        sa.Column("place_type", sa.String(64)),
        sa.Column("population", sa.Integer()),
        sa.Column("source", sa.String(256), nullable=False),
        sa.Column("geom", Geometry("POINT", srid=4326), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_settlements_geom", "settlements", ["geom"], postgresql_using="gist")

    op.create_table(
        "buildings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("osm_id", sa.BigInteger(), index=True),
        sa.Column("building_type", sa.String(128)),
        sa.Column("name", sa.String(256)),
        sa.Column("levels", sa.Integer()),
        sa.Column("height_m", sa.Float()),
        sa.Column("has_3d", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("source", sa.String(256), nullable=False),
        sa.Column("geom", Geometry("MULTIPOLYGON", srid=4326), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_buildings_geom", "buildings", ["geom"], postgresql_using="gist")

    op.create_table(
        "roads",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("osm_id", sa.BigInteger(), index=True),
        sa.Column("name", sa.String(256)),
        sa.Column("highway", sa.String(64), index=True),
        sa.Column("surface", sa.String(64)),
        sa.Column("source", sa.String(256), nullable=False),
        sa.Column("geom", Geometry("MULTILINESTRING", srid=4326), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_roads_geom", "roads", ["geom"], postgresql_using="gist")

    op.create_table(
        "points_of_interest",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("osm_id", sa.BigInteger(), index=True),
        sa.Column("name", sa.String(256), index=True),
        sa.Column("category", sa.String(128), index=True),
        sa.Column("subcategory", sa.String(128)),
        sa.Column("source", sa.String(256), nullable=False),
        sa.Column("geom", Geometry("POINT", srid=4326), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_poi_geom", "points_of_interest", ["geom"], postgresql_using="gist")

    op.create_table(
        "data_coverage",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("layer", sa.String(64), unique=True, nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("feature_count", sa.Integer()),
        sa.Column("has_3d", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("source", sa.String(256)),
        sa.Column("source_url", sa.Text()),
        sa.Column("notes", sa.Text()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Seed coverage rows as missing — UI must not invent presence
    op.execute(
        """
        INSERT INTO data_coverage (layer, status, feature_count, has_3d, notes) VALUES
        ('municipal_boundary', 'missing', 0, false, 'Awaiting verified OSM admin boundary import'),
        ('settlements', 'missing', 0, false, 'Awaiting OSM place nodes/polygons'),
        ('buildings', 'missing', 0, false, 'Awaiting OSM building footprints'),
        ('roads', 'missing', 0, false, 'Awaiting OSM highway network'),
        ('points_of_interest', 'missing', 0, false, 'Awaiting OSM amenities/POIs'),
        ('landuse', 'missing', 0, false, 'Not yet imported'),
        ('water', 'missing', 0, false, 'Not yet imported'),
        ('demographics', 'missing', 0, false, 'No open demographics series loaded'),
        ('3d_buildings', 'missing', 0, false, 'No real 3D coverage — Cesium must label missing')
        """
    )


def downgrade() -> None:
    op.drop_table("data_coverage")
    op.drop_index("ix_poi_geom", table_name="points_of_interest")
    op.drop_table("points_of_interest")
    op.drop_index("ix_roads_geom", table_name="roads")
    op.drop_table("roads")
    op.drop_index("ix_buildings_geom", table_name="buildings")
    op.drop_table("buildings")
    op.drop_index("ix_settlements_geom", table_name="settlements")
    op.drop_table("settlements")
    op.drop_index("ix_municipal_boundary_geom", table_name="municipal_boundary")
    op.drop_table("municipal_boundary")
