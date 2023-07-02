# Copyright (c) 2023, Crate.io Inc.
# Distributed under the terms of the AGPLv3 license, see LICENSE.
import pytest
from click.testing import CliRunner
from sqlalchemy.exc import ProgrammingError

from cratedb_retention.cli import cli
from tests.conftest import TESTDRIVE_DATA_SCHEMA


def test_version():
    """
    CLI test: Invoke `cratedb-retention --version`.
    """
    runner = CliRunner()

    result = runner.invoke(
        cli,
        args="--version",
        catch_exceptions=False,
    )
    assert result.exit_code == 0


def test_setup_brief(cratedb, caplog):
    """
    CLI test: Invoke `cratedb-retention setup`.
    """
    database_url = cratedb.get_connection_url()
    runner = CliRunner()

    result = runner.invoke(
        cli,
        args=f'setup "{database_url}"',
        catch_exceptions=False,
    )
    assert result.exit_code == 0

    assert 1 <= len(caplog.records) <= 2


def test_setup_verbose(cratedb, caplog):
    """
    CLI test: Invoke `cratedb-retention setup`.
    """
    database_url = cratedb.get_connection_url()
    runner = CliRunner()

    result = runner.invoke(
        cli,
        args=f'--verbose setup "{database_url}"',
        catch_exceptions=False,
    )
    assert result.exit_code == 0

    assert 3 <= len(caplog.records) <= 5


def test_list_policies(store, capsys):
    """
    Verify a basic DELETE retention policy through the CLI.
    """

    database_url = store.database.dburi
    runner = CliRunner()

    # Invoke data retention through CLI interface.
    result = runner.invoke(
        cli,
        args=f'list-policies "{database_url}"',
        catch_exceptions=False,
    )
    assert result.exit_code == 0

    # TODO: Can't read STDOUT. Why?
    """
    out, err = capsys.readouterr()
    output = json.loads(out)
    item0 = output[0]

    assert item0["table_schema"] == "doc"
    assert item0["table_name"] == "raw_metrics"
    """


def test_run_delete_basic(store, database, raw_metrics, policies):
    """
    Verify a basic DELETE retention policy through the CLI.
    """

    database_url = store.database.dburi
    runner = CliRunner()

    # Invoke data retention through CLI interface.
    result = runner.invoke(
        cli,
        args=f'run --cutoff-day=2024-12-31 --strategy=delete "{database_url}"',
        catch_exceptions=False,
    )
    assert result.exit_code == 0

    # Verify that records have been deleted.
    assert database.count_records(f'"{TESTDRIVE_DATA_SCHEMA}"."raw_metrics"') == 0


def test_run_delete_with_tags_match(store, database, sensor_readings, policies):
    """
    Verify a basic DELETE retention policy through the CLI, with using correct (matching) tags.
    """

    database_url = store.database.dburi
    runner = CliRunner()

    # Invoke data retention through CLI interface.
    result = runner.invoke(
        cli,
        args=f'run --cutoff-day=2024-12-31 --strategy=delete --tags=foo,bar "{database_url}"',
        catch_exceptions=False,
    )
    assert result.exit_code == 0

    # Verify that records have been deleted.
    assert database.count_records(f'"{TESTDRIVE_DATA_SCHEMA}"."sensor_readings"') == 0


def test_run_delete_with_tags_unknown(store, database, sensor_readings, policies):
    """
    Verify a basic DELETE retention policy through the CLI, with using wrong (not matching) tags.
    """

    database_url = store.database.dburi
    runner = CliRunner()

    # Invoke data retention through CLI interface.
    result = runner.invoke(
        cli,
        args=f'run --cutoff-day=2024-12-31 --strategy=delete --tags=foo,unknown "{database_url}"',
        catch_exceptions=False,
    )
    assert result.exit_code == 0

    # Verify that records have not been deleted, because the tags did not match.
    assert database.count_records(f'"{TESTDRIVE_DATA_SCHEMA}"."sensor_readings"') == 9


def test_run_reallocate(store, database, raw_metrics, policies):
    """
    CLI test: Invoke `cratedb-retention run --strategy=reallocate`.
    """

    database_url = store.database.dburi
    runner = CliRunner()

    # Invoke data retention through CLI interface.
    result = runner.invoke(
        cli,
        args=f'run --cutoff-day=2024-12-31 --strategy=reallocate "{database_url}"',
        catch_exceptions=False,
    )
    assert result.exit_code == 0

    # Verify that records have been deleted.
    # FIXME: Currently, the test for this strategy apparently does not remove any records.
    #        The reason is probably, because the scenario can't easily be simulated on
    #        a single-node cluster.
    assert database.count_records(f'"{TESTDRIVE_DATA_SCHEMA}"."raw_metrics"') == 6


def test_run_snapshot(store, database, sensor_readings, policies):
    """
    CLI test: Invoke `cratedb-retention run --strategy=snapshot`.
    """

    database_url = store.database.dburi
    runner = CliRunner()

    # Invoke data retention through CLI interface.
    # FIXME: This currently can not be tested, because it needs a snapshot repository.
    # TODO: Provide an embedded MinIO S3 instance.
    with pytest.raises(ProgrammingError):
        runner.invoke(
            cli,
            args=f'run --cutoff-day=2024-12-31 --strategy=snapshot "{database_url}"',
            catch_exceptions=False,
        )
