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
