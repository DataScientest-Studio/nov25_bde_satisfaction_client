
# dictionnaire pour typer mes attributs
MAPPING_REVIEWS = {
    "dynamic": "strict",
    "properties": {
        "id_review": {"type": "keyword"},
        "is_verified": {"type": "boolean"},
        "date_review": {"type": "date"},
        "id_user": {"type": "keyword"},
        "user_name": {
            "type": "text",
            "fields": {"raw": {"type": "keyword"}}
        },
        "user_review": {"type": "text"},
        "user_review_length": {"type": "integer"},
        "user_rating": {"type": "float"},
        "date_response": {"type": "date"},
        "enterprise_name": {
            "type": "text",
            "fields": {"raw": {"type": "keyword"}}
        },
        "enterprise_response": {"type": "text"},
        "enterprise_url": {"type": "keyword"},
        "enterprise_rating": {"type": "float"},
        "enterprise_review_number": {"type": "integer"},
        "enterprise_percentage_one_star": {"type": "integer"},
        "enterprise_percentage_two_star": {"type": "integer"},
        "enterprise_percentage_three_star": {"type": "integer"},
        "enterprise_percentage_four_star": {"type": "integer"},
        "enterprise_percentage_five_star": {"type": "integer"},
    },
}
