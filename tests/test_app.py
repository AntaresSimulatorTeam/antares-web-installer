from pathlib import Path

from _pytest.monkeypatch import MonkeyPatch

from antares_web_installer.app import App


class TestApp:
    def test_run(self) -> None:
        assert False

    def test_kill_running_server(self) -> None:
        # 1. Lancer un serveur
        # 2. Appeler la méthode kill_running_server
        # 3. Vérifier que le serveur a bien été tué
        assert False

    def test_install_files__from_scratch(self, tmp_path: Path) -> None:
        """
        Case where the target directory does not exist.
        """
        # Prepare the test resources
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        target_dir = tmp_path / "target"

        # Say we have dummy files in the source directory
        expected_files = ["dummy.txt", "folder/dummy2.txt"]
        for name in expected_files:
            dummy_file = source_dir / name
            dummy_file.parent.mkdir(parents=True, exist_ok=True)
            dummy_file.touch()

        # Run the test
        app = App(source_dir=source_dir, target_dir=target_dir)
        app.install_files()

        # Check the results
        for name in expected_files:
            assert (target_dir / name).exists(), f"File {name} must be copied"

    def test_install_files__update_config(self, datadir: Path, monkeypatch: MonkeyPatch) -> None:
        # Replace the original `check_version` method with a mock
        monkeypatch.setattr(App, "check_version", lambda _: "2.14")

        # Prepare the test resources
        source_dir = datadir.joinpath("install_files/source_files")
        target_dir = datadir.joinpath("install_files/target_files")
        old_config = (target_dir / "config.yaml").read_text()

        app = App(source_dir=source_dir, target_dir=target_dir)
        app.install_files()

        # Check that `dummy.txt` has been copied
        assert (target_dir / "dummy.txt").exists()

        # Check that the config file has been updated
        new_config = (target_dir / "config.yaml").read_text()
        assert old_config != new_config

    def test_copy_files(self) -> None:
        assert False

    def test_check_version(self, tmp_path: Path) -> None:
        # 3 cas à tester :
        # 1. Le programme exécutable n'existe pas => InstallError
        # 2. Le programme exécutable existe, mais le programme plante => InstallError
        # 3. Le programme exécutable existe et fonctionne => pas d'erreur
        assert False

    def test_create_icons(self) -> None:
        assert False

    def test_start_server(self) -> None:
        assert False
