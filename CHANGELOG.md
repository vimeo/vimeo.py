# Changelog

## [1.0.0] - 2018-02-06
### Changed
- Moving API requests over to use API v3.4. ([#111](https://github.com/vimeo/vimeo.py/pull/111))
- Moving uploads over to using the new tus protocol. ([#111](https://github.com/vimeo/vimeo.py/pull/111), [@peixian](https://github.com/peixian))

## [0.4.1] - 2017-11-09
### Added
- Checking free space quotas before making an upload. ([#106](https://github.com/vimeo/vimeo.py/pull/106), [@gabrielgisoldo](https://github.com/gabrielgisoldo))

## [0.4.0] - 2017-10-25
### Changed
- Deprecating the `upgrade_to_108`0` option on video uploads. ([#107](https://github.com/vimeo/vimeo.py/pull/107))
- Formatting code to PEP 8. ([#105](https://github.com/vimeo/vimeo.py/pull/105), [@gabrielgisoldo](https://github.com/gabrielgisoldo))

## [0.3.10] - 2017-06-23
### Added
- JSON filter on upload, replace, picture and text track methods. ([#102](https://github.com/vimeo/vimeo.py/pull/102), [@etienned](https://github.com/etienned))

### Fixed
- Some typos in some error handling. ([#94](https://github.com/vimeo/vimeo.py/pull/94), [@klang](https://github.com/klang))

## [0.3.8] - 2016-10-03
### Fixed
- Fixing a typo in an exception class.

## [0.3.7] - 2016-09-27
## [0.3.6] - 2016-08-29
### Added
- Handling of rate limit exceptions. ([#87](https://github.com/vimeo/vimeo.py/pull/87), [@williamroot](https://github.com/williamroot))

## [0.3.5] - 2016-08-29
### Fixed
- Fix for Requests >= 2.11.0. ([#89](https://github.com/vimeo/vimeo.py/pull/89), [@Calzzetta](https://github.com/Calzzetta))

## [v0.3.4] - 2016-05-04
### Fixed
- Logic bug in picture uploading. ([#83](https://github.com/vimeo/vimeo.py/issues/83))
- Updating some bad documentation in the readme. ([#82](https://github.com/vimeo/vimeo.py/pull/82), [@enzzc](https://github.com/enzzc))

## [v0.3.3] - 2016-02-22
### Added
- Allowing for file-like uploads. ([#79](https://github.com/vimeo/vimeo.py/pull/79), [@cmhedrick](https://github.com/cmhedrick))

### Fixed
- Fix for incorrect exception name.

## [0.3.1] - 2015-09-16
### Added
- Changes have been made in order to support Python 3. PyPi distribution now uses a single tar for both Python 2 and 3. If you experience issues running in Python 3, feel free to open an issue.

## [v0.3.0] - 2015-05-19
### Added
- The ability to provide the state parameter for the OAuth2
authentication flow.

### Changed
- Minor changes have been made to upload in order to better support
Python 3. This does not mark guaranteed coverage for Python 3 support, but
additional issues are invited for full support.

## [v0.2.1] - 2015-01-20
### Fixed
- Invalid comparison in progress check for uploads. ([#53](https://github.com/vimeo/vimeo.py/issues/53))

## [v0.2.0] - 2014-11-14
### Added
- This release adds support for Python 3 and contains minor bugfixes.

## [v0.1.1] - 2014-10-02
### Fixed
- Incorrect versions of requests being loaded that are incompatible with the timeout tuple.
- An install dependency was actually imported before we performed the installation steps.

## [v0.1.0] - 2014-10-02
### Added
- First release using the Python [requests](http://docs.python-requests.org/en/latest/) module

[1.0.0]: https://github.com/vimeo/vimeo.py/compare/0.4.1...1.0.0
[0.4.1]: https://github.com/vimeo/vimeo.py/compare/0.4.0...0.4.1
[0.4.0]: https://github.com/vimeo/vimeo.py/compare/0.3.10...0.4.0
[0.3.10]: https://github.com/vimeo/vimeo.py/compare/0.3.8...0.3.10
[0.3.8]: https://github.com/vimeo/vimeo.py/compare/0.3.7...0.3.8
[0.3.7]: https://github.com/vimeo/vimeo.py/compare/0.3.6...0.3.7
[0.3.6]: https://github.com/vimeo/vimeo.py/compare/0.3.5...0.3.6
[0.3.5]: https://github.com/vimeo/vimeo.py/compare/v0.3.4...0.3.5
[v0.3.4]: https://github.com/vimeo/vimeo.py/compare/v0.3.3...v0.3.4
[v0.3.3]: https://github.com/vimeo/vimeo.py/compare/0.3.1...v0.3.3
[0.3.1]: https://github.com/vimeo/vimeo.py/compare/v0.3.0...0.3.1
[v0.3.0]: https://github.com/vimeo/vimeo.py/compare/v0.2.1...v0.3.0
[v0.2.1]: https://github.com/vimeo/vimeo.py/compare/v0.2.0...v0.2.1
[v0.2.0]: https://github.com/vimeo/vimeo.py/compare/v0.1.1...v0.2.0
[v0.1.1]: https://github.com/vimeo/vimeo.py/compare/v0.1.0...v0.1.1
