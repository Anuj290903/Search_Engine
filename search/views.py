from collections import defaultdict
from django.shortcuts import render, HttpResponse
from .models import MyUser, MyEducation, MyExperience
from django.db.models import Q
import Levenshtein

THRESHOLD = 2

def tokenize_string(string):
    return set(string.lower().split())

def calculate_similarity(string1, string2):
    if not string1 or not string2:
        return 100
    return Levenshtein.distance(string1.lower(), string2.lower()) 

def fuzzy_match(query, user_ids_seen):
    tokens = tokenize_string(query)
    user_entities = MyUser.objects.all()
    user_fields = ['first_name', 'last_name', 'username', 'location', 'headline']
    fuzzy_results = []

    for token in tokens:
        for user in user_entities:
            school_name = MyEducation.objects.filter(user_id=user.id).first()
            experience = MyExperience.objects.filter(user_id=user.id).first()
            similarity = 100
            for field in user_fields:
                similarity = min(calculate_similarity(getattr(user, field), token), similarity)
            if school_name:    
                similarity = min(calculate_similarity(school_name.school_name, token), similarity)
            if experience:    
                similarity = min(calculate_similarity(experience.title, token), similarity)
                similarity = min(calculate_similarity(experience.company_name, token), similarity)
            if similarity <= THRESHOLD and user.id not in user_ids_seen:
                result = {
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'headline': user.headline,
                    'location': user.location,
                    'school_name': school_name.school_name if school_name else 'None',
                    'title': experience.title if experience else 'None',
                    'company_name': experience.company_name if experience else 'None',
                    'similarity': similarity
                }
                fuzzy_results.append(result)
                user_ids_seen.add(user)
    
    # Sort fuzzy_results by similarity (Levenshtein distance) in ascending order
    fuzzy_results.sort(key=lambda x: x['similarity'])

    return fuzzy_results[:50]

def index(request):
    return render(request, "index.html")

def identify_entity_types(query):
    tokens = query.split()
    entity_types = {}

    # Lookup in the User table
    user_fields = ['first_name', 'last_name', 'username', 'location', 'headline']
    user_query = Q()
    for token in tokens:
        for field in user_fields:
            user_query |= Q(**{f'{field}__istartswith': token})

    user_entities = MyUser.objects.filter(user_query)[:50]

    entity_types['users'] = user_entities

    # Lookup in the Education table
    education_fields = ['school_name']
    education_query = Q()
    for token in tokens:
        for field in education_fields:
            education_query |= Q(**{f'{field}__istartswith': token})

    education_entities = MyEducation.objects.filter(education_query)[:50]
    entity_types['education'] = education_entities

    # Lookup in the Experience table
    experience_fields = ['title', 'company_name']
    experience_query = Q()
    for token in tokens:
        for field in experience_fields:
            experience_query |= Q(**{f'{field}__istartswith': token})

    experience_entities = MyExperience.objects.filter(experience_query)[:50]
    entity_types['experience'] = experience_entities

    return entity_types

# For exact matches right now results are very fast, but for fuzzy matches it is very slow
# We can use inverted index to make it faster when scaling up the application
# Inverted index is a data structure that maps tokens to the set of entities that contain the token

def build_inverted_index(entity_entities):
    inverted_index = defaultdict(set)
    for entity in entity_entities:
        tokens = set()
        for field in entity._meta.fields:
            field_value = getattr(entity, field.name)
            if isinstance(field_value, str):
                tokens.add(field_value.lower())
        for token in tokens:
            inverted_index[token].add(entity.id)
    return inverted_index

def search(request):
    query = request.GET.get('q')
    entity_types = identify_entity_types(query)
    results = list()
    user_ids_seen = set()

    # Process user results
    user_results = entity_types['users']
    for user in user_results:
        if user.id not in user_ids_seen:
            school_name = MyEducation.objects.filter(user_id=user.id).first()
            experience = MyExperience.objects.filter(user_id=user.id).first()

            result = {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'headline': user.headline,
                'location': user.location,
                'school_name': school_name.school_name if school_name else 'None',
                'title': experience.title if experience else 'None',
                'company_name': experience.company_name if experience else 'None'
            }
            results.append(result)
            user_ids_seen.add(user.id)

    # Process education results
    education_results = entity_types['education']
    for edu_result in education_results:
        user_id = edu_result.user_id
        if user_id not in user_ids_seen:
            experience = MyExperience.objects.filter(user_id=user_id).first()
            user = MyUser.objects.get(id=user_id)

            result = {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'headline': user.headline,
                'location': user.location,
                'school_name': edu_result.school_name,
                'title': experience.title if experience else 'None',
                'company_name': experience.company_name if experience else 'None'
            }
            results.append(result)
            user_ids_seen.add(user_id)

    # Process experience results
    experience_results = entity_types['experience']
    for exp_result in experience_results:
        user_id = exp_result.user_id
        if user_id not in user_ids_seen:
            education = MyEducation.objects.filter(user_id=user_id).first()
            user = MyUser.objects.get(id=user_id)

            result = {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'headline': user.headline,
                'location': user.location,
                'school_name': education.school_name if education else 'None',
                'title': exp_result.title,
                'company_name': exp_result.company_name
            }
            results.append(result)
            user_ids_seen.add(user_id)

    # Sort and rank results
    query_parts = query.lower().split()
    def calculate_relevance(result):
        relevance_score = 0
        for part in query_parts:
            relevance_score += (
                10 * (result.get('first_name', '').lower().count(part) if isinstance(result, dict) and result.get('first_name') is not None else 0) +
                10 * (result.get('last_name', '').lower().count(part) if isinstance(result, dict) and result.get('last_name') is not None else 0) +
                5 * (result.get('title', '').lower().count(part) if isinstance(result, dict) and result.get('title') is not None else 0) +
                3 * (result.get('company_name', '').lower().count(part) if isinstance(result, dict) and result.get('company_name') is not None else 0) +
                4 * (result.get('school_name', '').lower().count(part) if isinstance(result, dict) and result.get('school_name') is not None else 0)
            )
        return relevance_score

    ranked_results = sorted(results, key=calculate_relevance, reverse=True)

    if len(ranked_results) < 50:
        fuzzy_results = fuzzy_match(query, user_ids_seen)  
        ranked_results = ranked_results + fuzzy_results  
        
    max_results = 50
    truncated_results = ranked_results[:max_results]

    return render(request, 'index.html', {
        'query': query,
        'ranked_results': truncated_results,
    })

def test_database_connection(request):
    try:
        objects_count = MyUser.objects.filter(first_name='John').count()
        return HttpResponse(f"Database connected! Found {objects_count} objects.")
    except Exception as e:
        return HttpResponse(f"Failed to connect to the database: {e}", status=500)
