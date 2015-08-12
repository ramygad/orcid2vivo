from unittest import TestCase
from tests import FIXTURE_PATH
from app.fundings import FundingCrosswalk
import orcid2vivo
import app.vivo_namespace as ns
from app.vivo_uri import HashIdentifierStrategy
from orcid2vivo import SimpleCreateEntitiesStrategy

from rdflib import Graph, RDFS
import vcr

my_vcr = vcr.VCR(
    cassette_library_dir=FIXTURE_PATH,
)


class TestFundings(TestCase):

    def setUp(self):
        self.graph = Graph(namespace_manager=ns.ns_manager)
        self.person_uri = ns.D["test"]
        self.create_strategy = SimpleCreateEntitiesStrategy(person_uri=self.person_uri)
        self.crosswalker = FundingCrosswalk(identifier_strategy=HashIdentifierStrategy(),
                                        create_strategy=self.create_strategy)


    @my_vcr.use_cassette('fundings/no.yaml')
    def test_no_funding(self):
        profile = orcid2vivo.fetch_orcid_profile('0000-0003-1527-0030')
        self.crosswalker.crosswalk(profile, self.person_uri, self.graph)
        # Assert no triples in graph
        self.assertTrue(len(self.graph) == 0)


    @my_vcr.use_cassette('fundings/with_funding.yaml')
    def test_with_funding(self):
        profile = orcid2vivo.fetch_orcid_profile('0000-0001-5109-3700')
        self.crosswalker.crosswalk(profile, self.person_uri, self.graph)
        # Verify a grant exists.
        grant_uri = ns.D['grant-9ea22d7c992375778b4a3066f5142624']
        self.assertEqual(
            self.graph.value(grant_uri, RDFS.label).toPython(),
            u"Policy Implications of International Graduate Students and Postdocs in the United States"
        )
        # Verify three PI roles related to grants for this person uri.
        pi_roles = [guri for guri in self.graph.subjects(predicate=ns.OBO['RO_0000052'], object=self.person_uri)]
        self.assertEqual(len(pi_roles), 3)
