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
