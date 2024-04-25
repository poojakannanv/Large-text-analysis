import json
import random
import pprint as pp
from copy import deepcopy
import requests
import pandas as pd 
from pyalex import config,Works, Authors, Sources, Institutions, Topics, Publishers, Funders
from dotenv import load_dotenv
import os
from flask import Flask, request, jsonify
from urllib.parse import quote_plus
from flask_cors import CORS
from datetime import *



app = Flask(__name__)
CORS(app)


API_KEY = 'AIzaSyDxfIQxxkklHytjLs9-hNyv0I4yNPvB_rk'
scopus_url = "https://api.elsevier.com/content/search/scopus"
crossref_url = "https://api.crossref.org/works"
semantic_scholar_url = "https://api.semanticscholar.org/graph/v1/paper/search/bulk"
openalex_url = "https://api.openalex.org/works"


load_dotenv()

semantic_key = os.getenv('semantic_key')
scopus_key = os.getenv('scopus_key')
email = os.getenv('email')


def get_scopus_results(query_term, limit):
    scopus_params = {
        'apiKey': scopus_key,
        'query': query_term,
        'count': limit,
    }
    try:
        scopus_response = requests.get(scopus_url, params=scopus_params)
        scopus_response.raise_for_status()  # Raise an exception for HTTP error codes
        scopus_original = deepcopy(scopus_response.json())
        return scopus_original
    except Exception as e:
        print(f"Error fetching Scopus results: {e}")
        return []

def get_crossref_results(query_term, limit):
    crossref_params = {
        'query': query_term,
        'rows': limit
    }
    try:
        crossref_response = requests.get(crossref_url, params=crossref_params)
        crossref_response.raise_for_status()
        crossref_original = deepcopy(crossref_response.json())
        return crossref_original
    except Exception as e:
        print(f"Error fetching Crossref results: {e}")
        return []

def get_semantic_scholar_results(query_term, limit):
    semantic_scholar_params = {
        'query': query_term,   
        'apiKey': semantic_key,
        'limit': limit,
        'fields': 'title,authors,year,referenceCount,externalIds,citationCount,publicationDate,abstract'
    }
    try:
        semantic_scholar_response = requests.get(semantic_scholar_url, params=semantic_scholar_params)
        semantic_scholar_response.raise_for_status()
        semantic_scholar_original = deepcopy(semantic_scholar_response.json())
        return semantic_scholar_original
    except Exception as e:
        print(f"Error fetching Semantic Scholar results: {e}")
        return []

def get_openalex_results(query_term, limit):
    params = {
        'filter': f'title.search:{query_term}',
        'mailto': email,
        'per-page': limit
    }
    try:
        open_alex = requests.get(openalex_url, params=params)
        open_alex.raise_for_status()
        openalex_original = deepcopy(open_alex.json())
        return openalex_original
    except Exception as e:
        print(f"Error fetching OpenAlex results: {e}")
        return []

#-------------------------------------------------------------------------------------------------------------------
# for each paper in each orginal api return insert a rank of where the paper came in that search output
def processing_indexing(source_input,source):
    if source == 'openalex':
       for index, paper in enumerate(source_input['results'], start=1):
            if source_input:
                paper[f'source_ranking_{source}'] = index
       random.shuffle(source_input['results'])
       return source_input

    elif source == 'semantic_scholar':
        for index, paper in enumerate(source_input['data'], start=1):
            if source_input:
                paper[f'source_ranking_{source}'] = index
        random.shuffle(source_input['data'])
        return source_input

    elif source == 'crossref':
        for index, paper in enumerate(source_input['message']['items'], start=1):
            if source_input:
                paper[f'source_ranking_{source}'] = index
        random.shuffle(source_input['message']['items'])
        return source_input
    
#-------------------------------------------------------------------------------------------------------------------



# processed_openalex = processing_indexing(get_openalex_results(query,10),"openalex")

# processed_crossref = processing_indexing(get_crossref_results(query,10),"crossref")

# processed_semantic_scholar = processing_indexing(get_semantic_scholar_results(query,10),"semantic_scholar")

#-------------------------------------------------------------------------------------------------------------------

def fetch_author_info(doi):
    url = f"https://api.crossref.org/works/{doi}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['message'].get('author', [])
    else:
        print(f"Failed to retrieve data for DOI: {doi}")
        return []
    
def fetch_openalex_author_info(doi):
    """
    Fetches author affiliation information from OpenAlex for a given DOI.
    """
    url = f"https://api.openalex.org/works?filter=doi:{doi}&mailto={email}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        authors_info = []
        if not data['results']:
            print(f"No results found for DOI: {doi}")
            return []
        for authorship in data['results'][0]['authorships']:
            author_name = authorship['author']['display_name']
            # Assuming the first institution as the primary affiliation
            affiliation = authorship['institutions'][0]['display_name'] if authorship['institutions'] else "No Affiliation"
            authors_info.append({
                'name': author_name,
                'affiliation': affiliation
            })
        return authors_info
    else:
        print(f"Failed to retrieve data for DOI: {doi}")
        return []

def get_combined_results(search_query):

    processed_openalex = processing_indexing(get_openalex_results(search_query,10),"openalex")

    processed_crossref = processing_indexing(get_crossref_results(search_query,10),"crossref")

    processed_semantic_scholar = processing_indexing(get_semantic_scholar_results(search_query,10),"semantic_scholar")

    return_id = 0

    combined_results = [] 
    for api_results in [processed_openalex,processed_crossref,processed_semantic_scholar]:
        if 'data' in api_results:
            # For Semantic Scholar API
            for paper in api_results['data'][:10]: # this limits the papers to 10 as the semantic scholar bulk endpoint doesnt have a limit, remove when completed  development 
                    
                    new_entry = {'title': paper['title']}
                    new_entry['return_id'] = return_id
                    return_id += 1
                    new_entry['date']  = paper.get('publicationDate')
                    new_entry['source'] = 'semantic_scholar'
                    new_entry['abstract'] = paper.get('abstract')
                    new_entry['source_ranking_semantic_scholar'] = paper.get('source_ranking_semantic_scholar')
                    new_entry['citationCount'] = paper.get('citationCount')
                    new_entry['DOI'] = paper['externalIds'].get("DOI")
                    new_entry['authors'] = [{'authorId': author['authorId'], 'name': author['name']} for author in paper['authors']]
                    combined_results.append(new_entry)




        elif 'message' in api_results and 'items' in api_results['message']:
            # For Crossref API
            for paper in api_results['message']['items']:
                    new_entry = {'title': paper['title'][0]}

                    if 'abstract' in paper:
                        new_entry['abstract'] = paper.get('abstract')
                    if not 'abstract' in paper:
                        continue
                    new_entry['return_id'] = return_id
                    return_id += 1
                    date_parts = paper['published']['date-parts'][0]
                    final_date = str(date(year=date_parts[0], month=date_parts[1], day=date_parts[2]))
                    new_entry['date'] = final_date
                    new_entry['source'] = 'CrossRef'
                    new_entry['is_referenced_by_count'] = paper.get('is-referenced-by-count')
                    new_entry['DOI'] = paper['DOI']
                    new_entry['authors'] = [{'given': author.get('given', 'N/A'), 'family': author.get('family', 'N/A')} for author in paper.get('author', [])]
                    new_entry['source_ranking_crossref'] = paper.get('source_ranking_crossref')  # Integration of source ranking field
                    combined_results.append(new_entry)



        elif 'search-results' in api_results and 'entry' in api_results['search-results']:
            # For Scopus API
            for paper in api_results['search-results']['entry']:

                    new_entry = {'title': paper['dc:title']}
                    new_entry['return_id'] = return_id
                    return_id += 1
                    new_entry['source'] = 'Scopus'
                    new_entry['citedby_count'] = paper.get('citedby-count')
                    new_entry['DOI'] = paper.get('prism:doi')
                    new_entry['authors'] = [{'given': author['given'], 'family': author['family']} for author in paper.get('author',[])]
                    new_entry['source_ranking_scopus'] = paper.get('source_ranking_scopus')  # Integration of source ranking field
                    combined_results.append(new_entry)

        if 'results' in api_results:
            open_alex_abstract = []
            for paper in api_results['results']:
                # Initialize new_entry as a dictionary with basic paper info
                new_entry = {
                    'title': paper['display_name'],
                    'return_id' : return_id,
                    'abstract' : [],
                    'source': 'OpenAlex',
                    'date' : paper['publication_date'],
                    'cited_by_count': paper['cited_by_count'],
                    'DOI': paper['doi'],
                    'authors': [],
                     'source_ranking_index' :paper['source_ranking_openalex']
                       # Initialize authors as an empty list
                }

                return_id += 1
                if paper.get('abstract_inverted_index') is not None:
                    flattened = [(word, pos) for word, positions in paper['abstract_inverted_index'].items() for pos in positions]
                    sorted_flattened = sorted(flattened, key=lambda x: x[1])
                    decoded_abstract = ' '.join(word for word, pos in sorted_flattened)
                    new_entry['abstract'] = decoded_abstract

                else:
                    new_entry['abstract'] = 'Abstract not available' 

                # Iterate through each authorship to append author details
                for authorship in paper['authorships']:
                    author_name = authorship['author']['display_name']
                    # Some authors may have multiple affiliations; we take the first one for simplicity.
                    affiliation_location = authorship['institutions'][0]['display_name'] if authorship['institutions'] else "No Affiliation"
                    # Append this author's details to the new_entry's authors list
                    new_entry['authors'].append({
                        'name': author_name,
                        'affiliation_location': affiliation_location
                    })
                
                # Append the fully constructed paper entry to combined_results
                combined_results.append(new_entry)

            


    dois_to_lookup = []
    for paper in combined_results:
        if paper['source'] not in ['OpenAlex']:
            doi = paper.get('DOI')
            if doi:
                dois_to_lookup.append(doi)






# Update combined_results_test directly
    for paper in combined_results:
        if paper.get('DOI') in dois_to_lookup:
            # Fetch new author information
            author_info = fetch_openalex_author_info(paper.get('DOI'))
            
            # Update the authors list for the matched paper
            updated_authors = []
            for author in author_info:
                author_name = author['name']  # Directly use the 'name' key
                author_affiliation = author.get('affiliation', 'No affiliation')  # Use the 'affiliation' key directly
                
                updated_authors.append({
                    'name': author_name,
                    'affiliation_location': author_affiliation
                })
                    
            
            # Replace the existing authors list with the updated one
            paper['authors'] = updated_authors

    random.shuffle(combined_results)

    return combined_results

def get_coordinates(address):
    """Convert an address into geographic coordinates using the Google Maps Geocoding API."""
    # Ensure the address is properly encoded to be included in the URL
    encoded_address = quote_plus(address)
    base_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={API_KEY}"

    response = requests.get(base_url)
    if response.status_code == 200:
        data = response.json()
        if data["status"] == "OK":
            # Extracting latitude and longitude
            latitude = data["results"][0]["geometry"]["location"]["lat"]
            longitude = data["results"][0]["geometry"]["location"]["lng"]
            return latitude, longitude
        else:
            return "Geocoding API error: " + data["status"]
    else:
        return "Request failed with status code " + str(response.status_code)





#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#filtering 


from rank_bm25 import BM25Okapi



def RankByAbstractBM25(query):
    results = get_combined_results(query)
    corpus = []
    for r in results:
        corpus.append(str(r.get('abstract')))

    tokenised_corpus = [doc.split(" ") for doc in corpus]
    bm25 = BM25Okapi(tokenised_corpus)

    tokenised_query = query.split(" ")

    scores = list(bm25.get_scores(tokenised_query))

    assert len(scores) == len(results)
    for (r,score) in zip(results,scores):
        r['bm25'] = score

    results.sort(key = lambda x: x['bm25'], reverse = True)

    return results



#results = get_combined_results('climate change')
#pp.pprint(results)

def RankByCitation(query):
    results = get_combined_results(query)
    for r in results:
        if 'cited_by_count' in r:
            try:
                r['rankcitation'] = int(r['cited_by_count'])
            except:
                r['rankcitation'] = 0
        elif 'citedby_count' in r:
            try:
                r['rankcitation'] = int(r['citedby_count'])
            except:
                r['rankcitation'] = 0
        elif 'is_referenced_by_count' in r:
            try:
                r['rankcitation'] = int(r['is_referenced_by_count'])
            except:
                r['rankcitation'] = 0
        elif 'citationCount' in r:
            try:
                r['rankcitation'] = int(r['citationCount'])
            except:
                r['rankcitation'] = 0

    results.sort(key=lambda x: x['rankcitation'], reverse=True)
    return results


def FilterByAuthor(query, searchAuthor):
    results = get_combined_results(query)
    results_filtered = []

    for r in results:
        authors = r['authors']
        for author in authors:
            if 'name' in author:
                if str(author.get('name')) == searchAuthor:
                    results_filtered.append(r)
                    break
            else:
                if str(author.get('author_name')) == searchAuthor:
                    results_filtered.append(r)
                    break

    return(results_filtered)

def parse_date(item):
    date = item['date']
    if isinstance(date, str):
        try:
            return datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            # Handle other date formats or set a default value if necessary
            return datetime.min.date()  # this sets invalid or missing dates to a far-past date
    return date

def sort_by_date(query,order):
    if order == 'DESC':
        sorted_data = sorted(
        (item for item in get_combined_results(query) if item['date'] is not None and parse_date(item) is not None),
        key=parse_date,reverse=True)
        return sorted_data
    elif order == 'ASC':
        sorted_data = sorted(
                        (item for item in get_combined_results(query) if item['date'] is not None and parse_date(item) is not None),
                        key=parse_date)
        return sorted_data

# for paper in get_combined_results("climate change"):
#     print(paper['date'],paper['source'])
#     print('-------')

# pp.pprint(sort_by_date("climate change",'DESC'))

    





        



@app.route('/filterselect', methods=['POST'])
def filter_select():
    data = request.json
    query = data.get('query', '')
    method = data.get('method','')
    author = data.get('author', '')
    date_order = data.get('date_order','')
    try:
        if method == "relevancy":
                    relevancy_rank = RankByAbstractBM25(query)
                    return jsonify(relevancy_rank)
        if method == "citation":
                    Citation_rank = RankByCitation(query)
                    return jsonify(Citation_rank)
        if method == 'FilterByAuthor':
                author_filter = FilterByAuthor(query, author)
                return jsonify(author_filter)
        if method == 'date_sort':
            return jsonify(sort_by_date(query,date_order))

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
    
 

            
         
         

         


@app.route('/search', methods=['POST'])
def search():
    data = request.json
    query = data.get('query', '')

    if not query:
        return jsonify({"error": "No query provided"}), 400

    try:
        results = get_combined_results(query)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

    
@app.route('/location', methods=['POST'])
def location():
    results = []
    data = request.json  # Assuming this comes from a Flask request
    candidates = data.get('candidates', [])

    if not candidates:
        return jsonify({"error": "No candidates provided"}), 400

    try:
        for candidate in candidates:
            title = candidate.get('title', 'No Title Provided')
            
            # Check if there are multiple authors
            if 'authors' in candidate:
                authors = candidate['authors']
            else:
                authors = [candidate.get('author', {})]

            for author in authors:
                author_name = author.get('name') or author.get('author_name', 'Unknown')
                affiliation = author.get('affiliation_location', 'No Affiliation')

                
                if affiliation != "No Affiliation":
                    coordinates = get_coordinates(affiliation)
                    results.append({
                        "title": title,
                        "author_name": author_name,
                        "affiliation_location": affiliation,
                        "lat_long": coordinates
                    })

        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


    
    

if __name__ == '__main__':
    app.run(debug=True)



 




#TODO
#real version














