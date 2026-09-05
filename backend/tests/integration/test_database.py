import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_postgres_connectivity(db_session: AsyncSession):
    """Verify raw PostgreSQL connection and basic query execution."""
    result = await db_session.execute(text("SELECT 1 AS num;"))
    val = result.scalar_one()
    assert val == 1


@pytest.mark.asyncio
async def test_postgis_extension_and_version(db_session: AsyncSession):
    """Verify PostGIS extension is installed and version is available."""
    result = await db_session.execute(text("SELECT PostGIS_Version();"))
    version_str = result.scalar_one()
    assert version_str is not None
    assert "3." in version_str  # PostGIS 3.x


@pytest.mark.asyncio
async def test_postgis_spatial_function(db_session: AsyncSession):
    """Verify PostGIS spatial constructor and GeoJSON output."""
    query = text("SELECT ST_AsGeoJSON(ST_SetSRID(ST_MakePoint(80.2458, 12.9716), 4326));")
    result = await db_session.execute(query)
    geojson_str = result.scalar_one()
    assert geojson_str is not None
    assert "Point" in geojson_str
    assert "80.2458" in geojson_str
    assert "12.9716" in geojson_str
