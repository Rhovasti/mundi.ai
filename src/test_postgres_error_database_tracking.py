# Copyright (C) 2025 Bunting Labs, Inc.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pytest


@pytest.mark.anyio
async def test_postgres_error_stored_in_database(auth_client):
    map_response = await auth_client.post(
        "/api/maps/create",
        json={
            "title": "Test Map for Database Error Tracking",
            "description": "Test map to verify error storage in database",
        },
    )
    assert map_response.status_code == 200
    map_data = map_response.json()
    project_id = map_data["project_id"]

    invalid_connection_uri = "postgresql://invalid:invalid@invalid.invalid:5432/invalid"
    add_connection_response = await auth_client.post(
        f"/api/projects/{project_id}/postgis-connections",
        json={
            "connection_uri": invalid_connection_uri,
            "connection_name": "Database Error Test Connection",
        },
    )
    assert add_connection_response.status_code == 200

    projects_response = await auth_client.get("/api/projects/")
    assert projects_response.status_code == 200
    projects_data = projects_response.json()

    test_project = None
    for project in projects_data["projects"]:
        if project["id"] == project_id:
            test_project = project
            break

    assert test_project is not None
    assert len(test_project["postgres_connections"]) == 1

    postgres_conn = test_project["postgres_connections"][0]
    assert "last_error_text" in postgres_conn
    assert "last_error_timestamp" in postgres_conn

    error_text = postgres_conn["last_error_text"]
    error_timestamp = postgres_conn["last_error_timestamp"]

    assert error_text is not None
    assert error_timestamp is not None

    assert error_text == "Unexpected error: [Errno -2] Name or service not known"
    assert error_timestamp is not None

    project_detail_response = await auth_client.get(f"/api/projects/{project_id}")
    assert project_detail_response.status_code == 200
    project_detail = project_detail_response.json()

    detail_postgres_conn = project_detail["postgres_connections"][0]
    assert detail_postgres_conn["last_error_text"] == error_text
    assert detail_postgres_conn["last_error_timestamp"] is not None
