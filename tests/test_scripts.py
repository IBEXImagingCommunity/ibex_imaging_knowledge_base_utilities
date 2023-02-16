import pytest
import pathlib
import hashlib

from ibex_imaging_knowledge_base_utilities.reagent_resources_csv_2_md_url import (
    csv_to_md_with_url,
)
from ibex_imaging_knowledge_base_utilities.fluorescent_probes_csv_2_md import (
    fluorescent_probe_csv_to_md,
)

from ibex_imaging_knowledge_base_utilities.bib2md import bibfile2md
from ibex_imaging_knowledge_base_utilities.update_index_md_stats import (
    update_index_stats,
)
from ibex_imaging_knowledge_base_utilities.validate_zenodo_json import (
    validate_zenodo_json,
)


class BaseTest:
    def setup_method(self):
        # Path to testing data is expected in the following location:
        self.data_path = pathlib.Path(__file__).parent.absolute() / "data"

    def files_md5(self, file_path_list):
        """
        Compute a single/combined md5 hash for a list of files.
        """
        md5 = hashlib.md5()
        for file_name in file_path_list:
            with open(file_name, "rb") as fp:
                for mem_block in iter(lambda: fp.read(128 * md5.block_size), b""):
                    md5.update(mem_block)
        return md5.hexdigest()


class TestCSV2MD(BaseTest):
    @pytest.mark.parametrize(
        "md_template_file_name, csv_file_name, supporting_material_root_dir, vendor_to_website_json_file_path, result_md5hash",  # noqa E501
        [
            (
                "reagent_resources.md.in",
                "reagent_resources.csv",
                "supporting_material",
                "vendors_and_urls.csv",
                "eaaff9000872870cfd0712ecc372f622",
            )
        ],
    )
    def test_csv_2_md_with_url(
        self,
        md_template_file_name,
        csv_file_name,
        supporting_material_root_dir,
        vendor_to_website_csv_file_path,
        result_md5hash,
    ):

        csv_to_md_with_url(
            self.data_path / md_template_file_name,
            self.data_path / csv_file_name,
            self.data_path / supporting_material_root_dir,
            self.data_path / vendor_to_website_csv_file_path,
        )
        assert (
            self.files_md5([(self.data_path / csv_file_name).with_suffix(".md")])
            == result_md5hash
        )


class TestFluorescentProbesCSV2MD(BaseTest):
    @pytest.mark.parametrize(
        "md_template_file_name, csv_file_name, result_md5hash",
        [
            (
                "fluorescent_probes.md.in",
                "fluorescent_probes.csv",
                "5a1133df3230beb235bc3e4eda324d90",
            )
        ],
    )
    def test_fluorescent_probe_csv_to_md(
        self, md_template_file_name, csv_file_name, result_md5hash, tmp_path
    ):
        fluorescent_probe_csv_to_md(
            template_file_path=self.data_path / md_template_file_name,
            csv_file_path=self.data_path / csv_file_name,
            output_dir=tmp_path,
        )
        assert self.files_md5([tmp_path / "fluorescent_probes.md"]) == result_md5hash


class TestBib2MD(BaseTest):
    @pytest.mark.parametrize(
        "bib_file_name, csl_file_name, result_md5hash",
        [("publications.bib", "ibex.csl", "b95a58740183fb04079027610e3d06c1")],
    )
    def test_bib_2_md(self, bib_file_name, csl_file_name, result_md5hash, tmp_path):
        # Write the output using the tmp_path fixture
        output_file_path = tmp_path / "publications.md"
        bibfile2md(
            self.data_path / bib_file_name,
            self.data_path / csl_file_name,
            output_file_path,
        )
        assert self.files_md5([output_file_path]) == result_md5hash


class TestUpdateIndexMDStats(BaseTest):
    @pytest.mark.parametrize(
        "input_md_file_name, csv_file_name, result_md5hash",
        [("index.md.in", "reagent_resources.csv", "776c99aec2968209d2e351e63e6b325a")],
    )
    def test_update_index_stats(
        self, input_md_file_name, csv_file_name, result_md5hash, tmp_path
    ):
        # Write the output using the tmp_path fixture
        output_dir = tmp_path
        update_index_stats(
            self.data_path / input_md_file_name,
            self.data_path / csv_file_name,
            output_dir,
        )
        assert self.files_md5([output_dir / pathlib.Path(input_md_file_name).stem]) == result_md5hash


class TestZenodoJsonValidataion(BaseTest):
    @pytest.mark.parametrize(
        "zenodo_json_file_name, result",
        [
            ("zenodo.json", 0),
            ("zenodo_duplicate_contributor.json", 1),
            ("zenodo_missing_orcid.json", 1),
        ],
    )
    def test_validate_zenodo_json(self, zenodo_json_file_name, result):
        assert validate_zenodo_json(self.data_path / zenodo_json_file_name) == result
