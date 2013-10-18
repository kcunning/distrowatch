import posixpath
import pkg_resources
import sys
from pip.download import url_to_path
from pip.exceptions import DistributionNotFound
from pip.index import PackageFinder, Link
from pip.log import logger
from pip.req import InstallRequirement
from pip.util import Inf


class MyPackageFinder(PackageFinder):
    
    def find_requirement(self, req, upgrade):
        url_name = req.url_name
        # Only check main index if index URL is given:
        main_index_url = None
        if self.index_urls:
            # Check that we have the url_name correctly spelled:
            main_index_url = Link(posixpath.join(self.index_urls[0], url_name))
            # This will also cache the page, so it's okay that we get it again later:
            page = self._get_page(main_index_url, req)
            if page is None:
                url_name = self._find_url_name(Link(self.index_urls[0]), url_name, req) or req.url_name

        # Combine index URLs with mirror URLs here to allow
        # adding more index URLs from requirements files
        all_index_urls = self.index_urls + self.mirror_urls

        def mkurl_pypi_url(url):
            loc = posixpath.join(url, url_name)
            # For maximum compatibility with easy_install, ensure the path
            # ends in a trailing slash.  Although this isn't in the spec
            # (and PyPI can handle it without the slash) some other index
            # implementations might break if they relied on easy_install's behavior.
            if not loc.endswith('/'):
                loc = loc + '/'
            return loc
        if url_name is not None:
            locations = [
                mkurl_pypi_url(url)
                for url in all_index_urls] + self.find_links
        else:
            locations = list(self.find_links)
        locations.extend(self.dependency_links)
        for version in req.absolute_versions:
            if url_name is not None and main_index_url is not None:
                locations = [
                    posixpath.join(main_index_url.url, version)] + locations

        file_locations, url_locations = self._sort_locations(locations)

        locations = [Link(url) for url in url_locations]
        logger.debug('URLs to search for versions for %s:' % req)
        for location in locations:
            logger.debug('* %s' % location)
        found_versions = []
        found_versions.extend(
            self._package_versions(
                [Link(url, '-f') for url in self.find_links], req.name.lower()))
        page_versions = []
        for page in self._get_pages(locations, req):
            logger.debug('Analyzing links from page %s' % page.url)
            logger.indent += 2
            try:
                page_versions.extend(self._package_versions(page.links, req.name.lower()))
            finally:
                logger.indent -= 2
        dependency_versions = list(self._package_versions(
            [Link(url) for url in self.dependency_links], req.name.lower()))
        if dependency_versions:
            logger.info('dependency_links found: %s' % ', '.join([link.url for parsed, link, version in dependency_versions]))
        file_versions = list(self._package_versions(
                [Link(url) for url in file_locations], req.name.lower()))
        if not found_versions and not page_versions and not dependency_versions and not file_versions:
            logger.fatal('Could not find any downloads that satisfy the requirement %s' % req)
            raise DistributionNotFound('No distributions at all found for %s' % req)
        if req.satisfied_by is not None:
            found_versions.append((req.satisfied_by.parsed_version, Inf, req.satisfied_by.version))
        if file_versions:
            file_versions.sort(reverse=True)
            logger.info('Local files found: %s' % ', '.join([url_to_path(link.url) for parsed, link, version in file_versions]))
            found_versions = file_versions + found_versions
        all_versions = found_versions + page_versions + dependency_versions
        applicable_versions = []
        for (parsed_version, link, version) in all_versions:
            if version not in req.req:
                logger.info("Ignoring link %s, version %s doesn't match %s"
                            % (link, version, ','.join([''.join(s) for s in req.req.specs])))
                continue
            applicable_versions.append((link, version))
        applicable_versions = sorted(applicable_versions, key=lambda v: pkg_resources.parse_version(v[1]), reverse=True)
        existing_applicable = bool([link for link, version in applicable_versions if link is Inf])
        if not upgrade and existing_applicable:
            if applicable_versions[0][1] is Inf:
                logger.info('Existing installed version (%s) is most up-to-date and satisfies requirement'
                            % req.satisfied_by.version)
            else:
                logger.info('Existing installed version (%s) satisfies requirement (most up-to-date version is %s)'
                            % (req.satisfied_by.version, applicable_versions[0][1]))
            return None
        if not applicable_versions:
            logger.fatal('Could not find a version that satisfies the requirement %s (from versions: %s)'
                         % (req, ', '.join([version for parsed_version, link, version in found_versions])))
            raise DistributionNotFound('No distributions matching the version for %s' % req)
        if applicable_versions[0][0] is Inf:
            # We have an existing version, and its the best version
            logger.info('Installed version (%s) is most up-to-date (past versions: %s)'
                        % (req.satisfied_by.version, ', '.join([version for link, version in applicable_versions[1:]]) or 'none'))
            return None
        if len(applicable_versions) > 1:
            logger.info('Using version %s (newest of versions: %s)' %
                        (applicable_versions[0][1], ', '.join([version for link, version in applicable_versions])))
        return applicable_versions


if __name__ == '__main__':
    req = InstallRequirement.from_line(sys.argv[1], None)
    print req, type(req)
    finder = MyPackageFinder([], ['http://pypi.python.org/simple/'])
    versions = finder.find_requirement(req, False)
    print 'Versions of %s' % sys.argv[1]
    for v in versions:
        print v[1]