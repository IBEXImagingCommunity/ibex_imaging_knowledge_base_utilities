import pytest
import pathlib
import hashlib

from ibex_imaging_knowledge_base_utilities.md_generation.bib2md import bibfile2md
from ibex_imaging_knowledge_base_utilities.md_generation.zenodo_json_2_thewho_md import (
    zenodo_creators_to_md,
)
from ibex_imaging_knowledge_base_utilities.md_generation.datadict_glossary_2_contrib_md import (
    dict_glossary_to_md,
)
from ibex_imaging_knowledge_base_utilities.md_generation.reagent_resources_csv_2_md_url import (
    csv_to_md_with_url,
)
from ibex_imaging_knowledge_base_utilities.md_generation.update_index_md_stats import (
    update_index_stats,
)
from ibex_imaging_knowledge_base_utilities.md_generation.fluorescent_probes_csv_2_md import (
    fluorescent_probe_csv_to_md,
)
from ibex_imaging_knowledge_base_utilities.csv_2_supporting import (
    csv_2_supporting,
)
from ibex_imaging_knowledge_base_utilities.md_generation.protocols_csv_2_md import (
    protocols_csv_to_md,
)
from ibex_imaging_knowledge_base_utilities.md_generation.videos_csv_2_md import (
    videos_csv_to_md,
)

from ibex_imaging_knowledge_base_utilities.data_validation.validate_zenodo_json import (
    validate_zenodo_json,
)

from ibex_imaging_knowledge_base_utilities.data_validation.validate_bib import (
    validate_bib_file_data,
)

import ibex_imaging_knowledge_base_utilities.data_validation.validate_basic as vbasic

import ibex_imaging_knowledge_base_utilities.data_validation.validate_videos as vvideos

from ibex_imaging_knowledge_base_utilities.data_validation.validate_reagent_resources import (
    validate_reagent_resources,
)
from ibex_imaging_knowledge_base_utilities.md_generation.data_software_csv_2_md import (
    data_software_csv_to_md,
)


class BaseTest:
    def setup_method(self):
        # Path to testing data is expected in the following location:
        self.data_path = pathlib.Path(__file__).parent.absolute() / "data"

    def files_md5(self, file_path_list):
        """
        Compute a single/combined md5 hash for a list of files. Open each file as text and use the read() method which
        to quote the documentation:
        In text mode, the default when reading is to convert platform-specific line endings (\n on Unix, \r\n on
        Windows) to just \n.

        This ensures that we get the same md5 hash on all platforms. If we opened the text files as binary the hashes
        become platform dependent (\r\n vs. \n).
        """
        md5 = hashlib.md5()
        for file_name in file_path_list:
            with open(file_name, "r") as fp:
                file_contents = fp.read()
                md5.update(file_contents.encode("utf-8"))
        return md5.hexdigest()


class TestCSV2MD(BaseTest):
    @pytest.mark.parametrize(
        "md_template_file_name, csv_file_name, supporting_material_root_dir, vendor_to_website_csv_file_path, result_md5hash",  # noqa E501
        [
            (
                "reagent_resources.md.in",
                "reagent_resources.csv",
                "supporting_material",
                "vendors_and_urls.csv",
                "612ec9d57ef4622f011628476e59a5e7",
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
                "5c223f6b6dd3856ae74bd6b99f915c8a",
            )
        ],
    )
    def test_fluorescent_probe_csv_to_md(
        self, md_template_file_name, csv_file_name, result_md5hash, tmp_path
    ):
        output_dir = tmp_path
        fluorescent_probe_csv_to_md(
            template_file_path=self.data_path / md_template_file_name,
            csv_file_path=self.data_path / csv_file_name,
            output_dir=output_dir,
        )
        assert (
            self.files_md5([output_dir / pathlib.Path(md_template_file_name).stem])
            == result_md5hash
        )


class TestBib2MD(BaseTest):
    @pytest.mark.parametrize(
        "bib_file_name, csl_file_name, result_md5hash",
        [("publications.bib", "ibex.csl", "25bef22343ba3a84b984c8c69faf95a8")],
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
        [("index.md.in", "reagent_resources.csv", "590ea41070c761836f96c87442e29fc6")],
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
        assert (
            self.files_md5([output_dir / pathlib.Path(input_md_file_name).stem])
            == result_md5hash
        )


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


class ZenodoJson2Contrib(BaseTest):
    @pytest.mark.parametrize(
        "input_md_file_name, zenodo_json_file_name, result_md5hash",
        [
            ("the_who.md.in", "zenodo.json", "cfc7c78033d0b88bfffde28c8b684f37"),
        ],
    )
    def test_zenodo_creators_to_md(
        self, input_md_file_name, zenodo_json_file_name, result_md5hash, tmp_path
    ):
        output_dir = tmp_path
        zenodo_creators_to_md(
            self.data / input_md_file_name,
            self.data_path / zenodo_json_file_name,
            output_dir,
        )
        assert (
            self.files_md5([output_dir / pathlib.Path(input_md_file_name).stem])
            == result_md5hash
        )


class TestDictGlossary2Contrib(BaseTest):
    @pytest.mark.parametrize(
        "input_md_file_name, dict_csv_file_name, glossary_csv_file_name, result_md5hash",
        [
            (
                "contrib.md.in",
                "reagent_data_dict.csv",
                "reagent_glossary.csv",
                "10783a53045a2691fb8719eaeb579eb1",
            )
        ],
    )
    def test_dict_glossary_to_md(
        self,
        input_md_file_name,
        dict_csv_file_name,
        glossary_csv_file_name,
        result_md5hash,
        tmp_path,
    ):
        # Write the output using the tmp_path fixture
        output_dir = tmp_path
        dict_glossary_to_md(
            self.data_path / input_md_file_name,
            self.data_path / dict_csv_file_name,
            self.data_path / glossary_csv_file_name,
            output_dir,
        )
        assert (
            self.files_md5([output_dir / pathlib.Path(input_md_file_name).stem])
            == result_md5hash
        )


class TestCSV2Supporting(BaseTest):
    @pytest.mark.parametrize(
        "csv_file, image_dir, supporting_template_file, output_file_paths, result_md5hash",
        [
            (
                "reagent_batch.csv",
                "image_dir",
                "supporting_template.md",
                [
                    "CD106_PE/0000-0003-4379-8967.md",
                    "CD20_AF488/0000-0001-9561-4256.md",
                    "FOXP3_eF570/0000-0003-4379-8967.md",
                    "Glutamine_synthetase_CoraLite_Plus_AF488/0000-0003-2088-8310.md",
                    "CD20_AF488/0000-0003-4379-8967.md",
                    "Granzyme_B_Unconjugated/0000-0001-9561-4256.md",
                    "Ki-67_BV510/0000-0001-9561-4256.md",
                ],
                "c3345fe77aa30a9e87ae15238729d561",
            )
        ],
    )
    def test_csv_to_supporting(
        self,
        csv_file,
        image_dir,
        supporting_template_file,
        output_file_paths,
        result_md5hash,
        tmp_path,
    ):
        # Write the output using the tmp_path fixture
        output_dir = tmp_path
        csv_2_supporting(
            self.data_path / csv_file,
            self.data_path / image_dir,
            output_dir,
            self.data_path / supporting_template_file,
        )
        assert (
            self.files_md5([output_dir / file_path for file_path in output_file_paths])
            == result_md5hash
        )


class TestProtocolsCSV2MD(BaseTest):
    @pytest.mark.parametrize(
        "md_template_file_name, csv_file_name, result_md5hash",
        [
            (
                "protocols.md.in",
                "protocols.csv",
                "ae265c655481dc8cabf540f82b804b71",
            )
        ],
    )
    def test_protocols_csv_to_md(
        self, md_template_file_name, csv_file_name, result_md5hash, tmp_path
    ):
        output_dir = tmp_path
        protocols_csv_to_md(
            template_file_path=self.data_path / md_template_file_name,
            csv_file_path=self.data_path / csv_file_name,
            output_dir=output_dir,
        )
        assert (
            self.files_md5([output_dir / pathlib.Path(md_template_file_name).stem])
            == result_md5hash
        )


class TestVideosCSV2MD(BaseTest):
    @pytest.mark.parametrize(
        "md_template_file_name, csv_file_name, result_md5hash",
        [
            (
                "videos.md.in",
                "videos.csv",
                "9aa31d29c6682b43c4c27aed856cf2dd",
            ),
        ],
    )
    def test_videos_csv_to_md(
        self, md_template_file_name, csv_file_name, result_md5hash, tmp_path
    ):
        output_dir = tmp_path
        videos_csv_to_md(
            template_file_path=self.data_path / md_template_file_name,
            csv_file_path=self.data_path / csv_file_name,
            output_dir=output_dir,
        )
        assert (
            self.files_md5([output_dir / pathlib.Path(md_template_file_name).stem])
            == result_md5hash
        )


class TestDataSetsSoftwareCSV2MD(BaseTest):
    @pytest.mark.parametrize(
        "md_template_file_name, datasets_csv_file_name, software_csv_file_name, result_md5hash",
        [
            (
                "data_and_software.md.in",
                "datasets.csv",
                "software.csv",
                "549b9840e26aad14509018b0c2b7b733",
            )
        ],
    )
    def test_datasets_software_csv_to_md(
        self,
        md_template_file_name,
        datasets_csv_file_name,
        software_csv_file_name,
        result_md5hash,
        tmp_path,
    ):
        output_dir = tmp_path
        data_software_csv_to_md(
            template_file_path=self.data_path / md_template_file_name,
            data_csv_file_path=self.data_path / datasets_csv_file_name,
            software_csv_file_path=self.data_path / software_csv_file_name,
            output_dir=output_dir,
        )
        assert (
            self.files_md5([output_dir / pathlib.Path(md_template_file_name).stem])
            == result_md5hash
        )


class TestBibfileValidataion(BaseTest):
    @pytest.mark.parametrize(
        "bibtex_file_name, result",
        [
            ("publications.bib", 0),
            ("duplicate_key.bib", 1),
            ("missing_key.bib", 1),
            ("syntax_error.bib", 1),
        ],
    )
    def test_validate_bibfile(self, bibtex_file_name, result):
        assert validate_bib_file_data(self.data_path / bibtex_file_name) == result


class TestBasicValidation(BaseTest):
    @pytest.mark.parametrize(
        "json_config, input_csv, result",
        [
            ("fluorescent_probes.json", "fluorescent_probes.csv", 0),
            ("fluorescent_probes.json", "fluorescent_probes_duplicates.csv", 1),
            (
                "fluorescent_probes.json",
                "fluorescent_probes_leading_trailing_whitespace.csv",
                1,
            ),
        ],
    )
    def test_validate_basic(self, json_config, input_csv, result):
        assert (
            vbasic.main(
                [str(self.data_path / input_csv), str(self.data_path / json_config)]
            )
            == result
        )


class TestVideosValidation(BaseTest):
    @pytest.mark.parametrize(
        "json_config, zenodo_json, input_csv, result",
        [
            ("videos.json", "zenodo.json", "videos.csv", 0),
            ("videos.json", "zenodo.json", "videos_with_unexpected_orcid.csv", 1),
        ],
    )
    def test_validate_videos(self, json_config, zenodo_json, input_csv, result):
        assert (
            vvideos.main(
                [
                    str(self.data_path / input_csv),
                    str(self.data_path / json_config),
                    str(self.data_path / zenodo_json),
                ]
            )
            == result
        )


class TestReagentResourcesValidation(BaseTest):
    @pytest.mark.parametrize(
        "json_config, input_csv, zenodo_json, vendor_csv, supporting_material_root_dir, result",
        [
            (
                "reagent_resources.json",
                "reagent_resources.csv",
                "zenodo.json",
                "vendors_and_urls.csv",
                "supporting_material",
                0,
            ),
        ],
    )
    def test_validate_reagent_resources(
        self,
        json_config,
        input_csv,
        zenodo_json,
        vendor_csv,
        supporting_material_root_dir,
        result,
    ):
        assert (
            validate_reagent_resources(
                str(self.data_path / input_csv),
                str(self.data_path / json_config),
                str(self.data_path / zenodo_json),
                str(self.data_path / vendor_csv),
                str(self.data_path / supporting_material_root_dir),
            )
            == result
        )
