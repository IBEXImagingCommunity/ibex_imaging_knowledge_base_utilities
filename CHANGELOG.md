# IBEX Knowledge-Base Utility Code Changelog

All notable changes to this package are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Each release should describe the changes using the following subsection types:
  * *Added* - new features.
  * *Changed* - changes in existing functionality.
  * *Deprecated* - soon to be removed features.
  * *Removed* - removed features.
  * *Fixed* - bug fixes.

When working on the package, add information under the "Unreleased" heading. In this manner the release notes are
created incrementally, and do not require a concerted effort prior to a release.

Using a manual approach to create the release notes instead of automatically deriving them from the
commits allows us to provide a high level description of the features and issues, yet provide details when those are
needed. This is equivalent to summarizing all activity on a feature branch versus reporting all commits on that branch.

## Unreleased

## v0.8.1

### Fixed
* validate_bib - incorrect argument name used in main (args.zenodo_json when it should be args.bibfile).
* validate_image_resources - use of relative path instead of absolute path resulted in incorrect mismatches between filenames from csv and actual files on disk, changed to absolute path resolved the issue.

## v0.8.0

### Added
* validate_reagent_resources - Validation script which checks that the reagent_resources.csv file is valid. Runs the validate_basic code followed by validation specific to the expectations from the reagent_resources.csv contents. 
* validate_image_resources - Validation script which checks that the image_resources.csv file is valid (runs the validate_basic code) and that the corresponding images found in the supporting_material directory of the Knowledge-Base are not corrupt (compare the md5 hash listed in the csv file to the md5 hash of the image file on disk).
* validate_videos - Validation script which checks that the videos.csv file is valid. Performs basic validation after obtaining the ORCIDs from the .zenodo.json file to ensure that the contributors listed in the csv file are listed in the zenodo config file. This ensures that we give credit where it is due.
* validate_bibfile - Validation script which checks that the bibliography file is valid (duplicate citation keys, syntax errors). Beyond general validity it enforces some Knowlege-Base specific requirements (doi, and note fields are required though in most contexts they are optional).
* validate_basic - Basic validation script for csv files. The script is configured via a json file containing the following dictionary:
  * data_required_column_names - Columns that cannot contain empty entries.
  * data_optional_column_names - Columns that may contain empty entries. Together with the data_required_column_names these list all of the expected column names.
  * unique_entry_columns - columns that cannot contain duplicates.
  * url_columns - columns containing a single url. Check for existence, no 404.
  * multi_url_columns - columns containing multiple urls per column with semicolon separating between them. Check for existence, no 404.
  * doi_columns - columns containing a single DOI (URL is constructed as `https://doi.org/{doi}`). Check for existence, no 404.
  * multi_doi_columns - columns containing multiple DOIs separated by semicolons (URL is constructed as `https://doi.org/{doi}`). Check for existence, no 404.
  * column_is_in - columns containing a single entry that has to be in the specified set of values.
  * multi_value_column_is_in - columns containing multiple entries separated by semicolons that have to be in the specified set of values.

## v0.7.0

### Added
* data_software_csv_2_md - Utility script which converts the datasets.csv and software.csv data to the markdown file used by the site.

### Fixed
* csv files in which a cell contained multi-paragraph text were not written as expected to markdown when using the pandas dataframe `to_markdown` method. This is because the markdown format does not support newlines in a table cell, though it does work with html `<br>` tag. The utilities module provides a wrapper function `_dataframe_2_md` which first replaces all newlines with the html tag `<br>`. All additional parameters given to the method are forwarded to the pandas `to_markdown` method (an alternative option would be to decorate the pandas dataframe method).

## v0.6.0

### Added
* videos_csv_2_md - Utility script which converts the videos.csv data to the markdown file used by the site.

### Changed
* validate_zenodo_json - Additional validation, check that the listed ORCIDs have corresponding pages on [https://orcid.org/](https://orcid.org/).

## v0.5.0

### Added
* protocols_csv_2_md - Utility script which converts the protocols.csv data to the markdown file used by the site.
* csv_2_supporting - Utility script which enables batch creation of supporting material files from a csv file with similar structure to the reagent_resources.csv plus two additional columns "Publications" and "Notes".

## v0.4.1

### Fixed
* reagent_resources_csv_2_md_url - Paths to supporting file names cannot contain any of the following characters: " ", "\t", "/", "\", "{", "}", "[", "]", "(", ")", "<", ">", ":", "&". All of them are replaced with underscore. Previously "&" was not replaced and it caused problems linking to the supporting material files.
* datadict_glossary_2_contrib_md - Insertion of tables into the input markdown file is done via the string `replace` and not the `format` method because the use of `format` precludes the presence of curly braces in the template file. We now need to use curly braces in the input contrib markdown file.

## v0.4.0

### Added
* zenodo_json_2_thewho_md - Explicitly list all of the contributors to the knowledge base. The list is extracted from the .zenodo.json file and inserted into the given markdown template file, ends with `md.in`.
* datadict_glossary_2_contrib_md - Script which creates the contrib.md file, instructions on how to contribute. The file is created from a template input file, the knowledge base data dictionary and glossary csv files.

### Changed
* reagent_resources_csv_2_md_url - Use a csv file to map vendor name to URL instead of a JSON file. Treat it as data and not as a program configuration file.
* update_index_md_stats - Use output directory instead of output file name. File name is derived from input file name which ends with `.md.in`.
* fluorescent_probes_csv_2_md - Change fluorescent probes table alignment to left align and derive output file name from input which ends with `.md.in`.

## v0.3.2

### Changed
* reagent_resources_csv_2_md_url - Update the automatic path to supporting material creation. The paths cannot include parentheses, so those are replaced with underscores. Additionally, the insertion of the table into the input markdown file is done via the string `replace` and not the `format` method because the use of `format` precludes the presence of curly braces in the template file. We now need to use curly braces in the input markdown file so that the table has an id value when the markdown is converted to html.

## v0.3.0

### Added
* fluorescent_probes_csv_2_md - script for creating the knowledge-base fluorescent_probes markdown page from the fluorescent_probes.csv.

### Changed
* reagent_resources_csv_2_md_url - In addition to the reagent_resources.csv we now use a template file into which the table is written. Allows us to modify the descriptive text without modifying code. Additionally, the table is sorted on the "Target Name / Protein Biomarker" column.
* update_index_md_stats - Change the computed statistics to:
  1. number_of_contributors - count both original contributors and folks that replicated the work.
  1. number_of_validated_reagents - count rows in the reagent_resources.csv.
  1. number_of_fluorescent_probes - count number of unique entries in conjugate column of the reagent_resources.csv (ignoring NA, Unconjugated, Biotin, HRP, UT014, UT015, UT016, UT019).
  1. number_of_tissues - count unique combinations of Target_Species-Target_Tissue-Tissue_State.

## v0.2.0

### Added
* validate_zenodo_json - script for validating the .zenodo.json file. Ensure that complies with our project specific requirements.

### Changed
* reagent_resources_csv_2_md_url - replace usage of spaces and slashs in paths with underscores, to match the structure of the `supporting_material` directory.

## v0.1.0

### Added
* bib2md - script for creating the knowledge-base publications markdown page from the publications.bib file.
* reagent_resources_csv_2_md_url - script for creating knowledge-base reagent_resources markdown page from the reagent_resources.csv.
* update_index_md_stats - script for updating the knowledge-base landing page with the current data statistics. 
