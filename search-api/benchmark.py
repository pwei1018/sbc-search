# Copyright © 2020 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tools for testing database performance."""

import time

from sqlalchemy.sql import literal_column
from sqlalchemy.dialects import oracle
from werkzeug.datastructures import ImmutableMultiDict

from search_api import create_app
from search_api.models.base import db
from search_api.models.corp_party import CorpParty
from search_api.models.corporation import Corporation

# Compare original COBRS system performance.
COBRS_SQL = """SELECT
       UPPER(LAST_NME)
      ,UPPER(FIRST_NME)
      ,P.CORP_NUM
      ,CASE  PARTY_TYP_CD       WHEN 'FIO' THEN 'OWNER'
                                WHEN 'DIR' THEN 'DIR'
                                ELSE 'OFF' END AS TITLE
    #   , CASE OS.OP_STATE_TYP_CD WHEN 'ACT' THEN 'A'
    #                             ELSE 'H' END AS STATUS
      ,CORP_PARTY_ID
      ,CORP_CLASS
  FROM CORP_PARTY P
      ,CORP_STATE S
      ,CORP_OP_STATE OS
      ,CORPORATION  C
      ,CORP_TYPE    CT
WHERE
    UPPER(FIRST_NME) LIKE 'JOHN'
    AND UPPER(LAST_NME) LIKE 'SMITH'
    AND PARTY_TYP_CD != 'OFF'
    AND P.END_EVENT_ID IS NULL
    AND P.CORP_NUM = S.CORP_NUM
    AND S.END_EVENT_ID IS NULL
    AND S.STATE_TYP_CD = OS.STATE_TYP_CD
    AND S.CORP_NUM = C.CORP_NUM
    AND C.CORP_TYP_CD = CT.CORP_TYP_CD
    AND ROWNUM <= 165
ORDER BY UPPER(LAST_NME)
#, UPPER(FIRST_NME), STATUS,CORP_CLASS,CORP_NUM DESC
"""

# Director search sql example.
DS_OPT = """
SELECT corp_party.corp_party_id,
       corp_party.first_nme,
       corp_party.middle_nme,
       corp_party.last_nme,
       corp_party.appointment_dt,
       corp_party.cessation_dt,
       corp_party.corp_num,
       corp_party.party_typ_cd,
       corp_name.corp_nme
FROM   corp_party
       LEFT OUTER JOIN corporation
         ON corporation.corp_num = corp_party.corp_num
       LEFT OUTER JOIN corp_state
         ON corp_state.corp_num = corp_party.corp_num
            AND corp_state.end_event_id IS NULL
       LEFT OUTER JOIN corp_name
                    ON corp_name.end_event_id IS NULL
                       AND corp_name.corp_name_typ_cd IN (
                           'CO', 'NB' )
                       AND corporation.corp_num = corp_name.corp_num
WHERE  corp_party.party_typ_cd != 'OFF'
       AND Upper(corp_party.first_nme) = 'JOHN'
       AND Upper(corp_party.last_nme) = 'SMITH'
       AND rownum <= 165
ORDER  BY Upper(corp_party.last_nme) DESC
"""


def _benchmark(start_time, result_set):
    """Benchmark utility"""
    if hasattr(result_set, 'statement'):
        oracle_dialect = oracle.dialect(max_identifier_length=30)
        raw_sql = str(result_set.statement.compile(dialect=oracle_dialect))
        print(raw_sql)

    count = 0
    for row in result_set:
        if count >= 50:
            break
        print(row)
        count += 1
    print('raw query time:', time.time() - start_time, ' number of results >=:', count)


def corporations():
    """Search corporations"""
    return (
        Corporation.search_corporations(
            ImmutableMultiDict(
                [
                    ('query', 'countable'),
                    ('page', '1'),
                    ('sort_type', 'dsc'),
                    ('sort_value', 'corpNme'),
                ]
            )
        )
        .filter(literal_column('rownum') <= 165)
    )


def corp_party_search():
    """Search Corp Party"""

    args = ImmutableMultiDict(
        [
            ('field', 'firstNme'),
            ('operator', 'exact'),
            ('value', 'JOHN'),
            ('field', 'lastNme'),
            ('operator', 'exact'),
            ('value', 'SMITH'),
            ('mode', 'ALL'),
            ('page', '1'),
            ('sort_type', 'dsc'),
            ('sort_value', 'lastNme'),
            ('additional_cols', 'none'),
        ]
    )

    return (
        CorpParty.search_corp_parties(args)
        .filter(literal_column('rownum') <= 165)
    )


def corp_party_similar_search():
    """Search Corp Party by similar"""

    args = ImmutableMultiDict(
        [
            ('field', 'firstNme'),
            ('field', 'lastNme'),
            ('operator', 'similar'),
            ('operator', 'exact'),
            ('value', 'john'),
            ('value', 'smith'),
            ('mode', 'ALL'),
            ('additional_cols', 'none'),
            ('page', '1'),
            ('sort_type', 'dsc'),
            ('sort_value', 'lastNme'),
        ]
    )

    return (
        CorpParty.search_corp_parties(args)
        .filter(literal_column('rownum') <= 165)
    )


def corp_party_nickname_search():
    """Search Corp Party by nickname"""

    args = ImmutableMultiDict(
        [
            ('field', 'firstNme'),
            ('field', 'lastNme'),
            ('operator', 'nicknames'),
            ('operator', 'exact'),
            ('value', 'john'),
            ('value', 'smith'),
            ('mode', 'ALL'),
            ('additional_cols', 'none'),
            ('page', '1'),
            ('sort_type', 'dsc'),
            ('sort_value', 'lastNme'),
        ]
    )

    return (
        CorpParty.search_corp_parties(args)
        .filter(literal_column('rownum') <= 165)
    )


def corp_party_2param_search():
    """Corp party 2 params"""
    args = ImmutableMultiDict(
        [
            ('field', 'firstNme'),
            ('field', 'lastNme'),
            ('operator', 'startswith'),
            ('operator', 'startswith'),
            ('value', 'clark'),
            ('value', 'van'),
            ('mode', 'ALL'),
            ('additional_cols', 'none'),
            ('page', '1'),
            ('sort_type', 'dsc'),
            ('sort_value', 'lastNme'),
        ]
    )
    return (
        CorpParty.search_corp_parties(args)
        .filter(literal_column('rownum') <= 165)
    )


def corp_party_addr_search():
    """Search Corp Party by Address"""

    args = ImmutableMultiDict(
        [
            # ('field', 'firstNme'),
            # ('operator', 'exact'),
            # ('value', 'donna'),
            ('field', 'addrLine1'),
            ('operator', 'contains'),
            ('value', '123 main st'),
            ('mode', 'ALL'),
            ('page', '1'),
            ('sort_type', 'dsc'),
            ('sort_value', 'lastNme'),
            ('additional_cols', 'none'),
        ]
    )

    return (
        CorpParty.search_corp_parties(args)
        .filter(literal_column('rownum') <= literal_column('165'))
    )


def corp_party_postal_cd_search():
    """Search Corp Party by Postal Code"""
    # Notes -
    # Ideally we'd like an index of UPPER(TRIM(POSTAL_CD)) for address.
    # Instead, the implementation is to try the 2 common versions. Uppercase with a space and
    # uppercase without.
    args = ImmutableMultiDict(
        [
            ('field', 'postalCd'),
            ('operator', 'exact'),
            ('value', 'V0H2B0'),
            ('mode', 'ALL'),
            ('page', '1'),
            ('sort_type', 'dsc'),
            ('sort_value', 'lastNme'),
            ('additional_cols', 'none'),
        ]
    )

    return (
        CorpParty.search_corp_parties(args)
        .filter(literal_column('rownum') <= 165)
    )


def benchmark_raw_sql(sql):
    """Benchmark raw SQL"""
    sql = '\n'.join([s for s in sql.split('\n') if '#' not in s])
    return db.session.execute(sql)


SQL = """
SELECT 1 FROM CORP_PARTY WHERE ROWNUM = 1
"""

if __name__ == '__main__':

    app = create_app('benchmark')  # pylint: disable=invalid-name
    with app.app_context():

        # The DB performs more consistently when a query has recently been made.
        print('warmup')
        t = time.time()
        rs = benchmark_raw_sql(SQL)
        _benchmark(t, rs)

        print('cobrs')
        t = time.time()
        rs = benchmark_raw_sql(COBRS_SQL)
        _benchmark(t, rs)

        # t = time.time()
        # rs = corp_party_addr_search()
        # _benchmark(t, rs)

        # t = time.time()
        # rs = corp_party_search()
        # _benchmark(t, rs)

        t = time.time()
        rs = benchmark_raw_sql(DS_OPT)
        _benchmark(t, rs)

        # t = time.time()
        # rs = corp_party_postal_cd_search()
        # _benchmark(t, rs)

        # t = time.time()
        # rs = corp_party_nickname_search()
        # _benchmark(t, rs)

        # t = time.time()
        # rs = corp_party_similar_search()
        # _benchmark(t, rs)

        # t = time.time()
        # rs = corporations()
        # _benchmark(t, rs)
