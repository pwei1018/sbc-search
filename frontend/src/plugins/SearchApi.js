import ApiService from "@/plugins/ApiService.js";

const PERSON_SEARCH_URL = "/person/search";
const COPRPARTY_SEARCH_URL = "/person";

export function searchApi(params) {
  console.log("Params", params);
  return ApiService.get(PERSON_SEARCH_URL, {
    params: params
  });
}

export function advancedSearchApi(query) {
  return ApiService.get(`${PERSON_SEARCH_URL}/?${query}`);
}

export function searchApiV2(params, { type }) {
  if (type === "basic") {
    console.log("Basic");
    return searchApi(params);
  } else if (type === "advanced") {
    return advancedSearchApi(params);
  }
}

export function corpPartySearch(id) {
  return ApiService.get(`${COPRPARTY_SEARCH_URL}/${id}`);
}
