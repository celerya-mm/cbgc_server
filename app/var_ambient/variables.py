_url = 'http://127.0.0.1:5000'

apiUrls_admin = {
    'admin_login':      f'{_url}/api/admin_login/',
    'admin_signup':     f'{_url}/api/admin_signup/',
    'admin_list':       f'{_url}/api/admins/',
    'admin_search':     f'{_url}/api/admin/<int:admin_id>',
}

apiUrls_user = {
    'user_login':       f'{_url}/api/user_login/',
    'user_signup':      f'{_url}/api/user_signup/',
    'user_list':        f'{_url}/api/users/',
    'user_search':      f'{_url}/api/user/<int:user_id>',
}

apiUrls_farmer = {
    'farmer_list':     f'{_url}/api/farmers/',
    'farmer_search':   f'{_url}/api/farmer/<int:farmer_id>',
}

apiUrls_buyer = {
    'buyer_list':     f'{_url}/api/buyers/',
    'buyer_search':   f'{_url}/api/buyer/<int:buyer_id>',
}

apiUrls_slaughterhouse = {
    'slaughterhouse_list':     f'{_url}/api/slaughterhouses/',
    'slaughterhouse_search':   f'{_url}/api/slaughterhouse/<int:slaughterhouse_id>',
}

apiUrls_head = {
    'head_list':     f'{_url}/api/heads/',
    'head_search':   f'{_url}/api/head/<int:head_id>',
}

apiUrls_certificate_DNA = {
    'certificate_dna_list':     f'{_url}/api/certificates_dna/',
    'certificate_dna_search':   f'{_url}/api/certificate_dna/<int:certificate_dna_id>',
}

apiUrls_certificate_CONS = {
    'certificate_cons_list':     f'{_url}/api/certificates_cons/',
    'certificate_cons_search':   f'{_url}/api/certificate_cons/<int:certificate_cons_id>',
}

colors = {
    "blue":         "#2B4692",
    "blue_light_1": "#3976C6",
    "blue_light_2": "#9BB5E8",
    "grey":         "#5B5A5B",
    "grey_light":   "#DEDEDE",
    "green":        "#2ACC7B",
    "red":          "#ED6666",
    "yellow":       "#F6D11B",
}
