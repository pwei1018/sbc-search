# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests for the Entity model.

Test suite to ensure that the Entity model routines are working as expected.
"""

import datetime
from sqlalchemy import func
from werkzeug.datastructures import ImmutableMultiDict

from search_api.models.corporation import Corporation
from search_api.models.corp_party import CorpParty
from search_api.models.nickname import NickName


DEFAULT_DATE = datetime.datetime.now() + datetime.timedelta(weeks=-1)


def test_corporation(session):
    """Assert that an Entity can be stored in the service."""
    corporation = Corporation(corp_num='BC1234567', recognition_dts=DEFAULT_DATE, corp_typ_cd='C')
    session.add(corporation)
    session.commit()
    assert corporation.corp_num is not None
    assert corporation.corp_typ_cd == 'C'


def test_corporation_search(session):  # pylint: disable=unused-argument
    """Assert that Corporations can be found by name or number."""
    results = Corporation.query_corporations('Pembina Pipeline', 'corpNme', None, 'corp_num')
    assert results.count() == 1

    results = Corporation.query_corporations('Pembina', 'corpNme', None, 'corp_num')
    assert results.count() == 1

    results = Corporation.query_corporations('Pipeline', 'corpNme', None, 'corp_num')
    assert results.count() == 1

    # corp num search disabled for perf.
    # results = Corporation.query_corporations('1234567890', None, 'corp_num')
    # assert results.count() == 1


def test_corp_party_search(session):  # pylint: disable=unused-argument
    """Assert that CorpParty entities can be found by name."""
    args = ImmutableMultiDict(
        [
            ('field', 'lastNme'),
            ('operator', 'exact'),
            ('value', 'PATTERSON'),
            ('mode', 'ALL'),
            ('page', '1'),
            ('sort_type', 'dsc'),
            ('sort_value', 'lastNme'),
            ('additional_cols', 'none'),
        ]
    )
    results = CorpParty.search_corp_parties(args).limit(50)
    assert results.count() == 2
    assert results[0].last_nme == 'PATTERSON'
    assert results[1].last_nme == 'Patterson'


def test_corp_party_same_addr(session):  # pylint: disable=unused-argument
    """Assert that CorpParty entities at same address can be found."""
    results = CorpParty.get_corp_party_at_same_addr(1)
    assert results.count() == 1


def test_corp_party_offices(session):  # pylint: disable=unused-argument
    """Assert that offices held by CorpParty can be found."""
    offices = CorpParty.get_offices_held_by_corp_party_id(1)
    assert len(offices) == 2


def test_corp_party_nicknames(session):
    """Assert that CorpParty nicknames can be found."""
    aliases = session.query(NickName.name).filter(
        NickName.name_id == session.query(NickName.name_id).filter(NickName.name == 'LILI')
    )

    alias_list = list(a[0] for a in aliases)
    assert len(alias_list) == 3

    results = CorpParty.query.filter(func.upper(CorpParty.first_nme).in_(alias_list))
    assert results.count() == 2
