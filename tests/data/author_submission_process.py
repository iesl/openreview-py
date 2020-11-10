def process(client, note, invitation):
    venue_id='.TMLR'

    paper_group=client.post_group(openreview.Group(id=f'{venue_id}/Paper{note.number}',
        readers=[venue_id],
        writers=[venue_id],
        signatures=[venue_id],
        signatories=[venue_id]
    ))

    authors_group_id=f'{paper_group.id}/Authors'
    authors_group=client.post_group(openreview.Group(id=authors_group_id,
        readers=[venue_id, authors_group_id],
        writers=[venue_id],
        signatures=[venue_id],
        signatories=[venue_id, authors_group_id],
        members=note.content['authorids']['value']
    ))

    action_editors_group_id=f'{paper_group.id}/AEs'
    action_editors_group=client.post_group(openreview.Group(id=action_editors_group_id,
        readers=[venue_id, action_editors_group_id],
        nonreaders=[authors_group_id],
        writers=[venue_id],
        signatures=[venue_id],
        signatories=[venue_id, action_editors_group_id],
        members=[]
    ))

    reviewers_group_id=f'{paper_group.id}/Reviewers'
    reviewers_group=client.post_group(openreview.Group(id=reviewers_group_id,
        readers=[venue_id, action_editors_group_id],
        nonreaders=[authors_group_id],
        writers=[venue_id, action_editors_group_id],
        signatures=[venue_id],
        signatories=[venue_id],
        members=[]
    ))

    ## TODO: create this invitation using an invitation
    review_invitation_id=f'{paper_group.id}/-/Review'
    invitation = client.post_invitation_edit(readers=[venue_id],
        writers=[venue_id],
        signatures=[venue_id],
        invitation=openreview.Invitation(id=review_invitation_id,
            invitees=[f"{paper_group.id}/Reviewers", f'{paper_group.id}/AEs'],
            readers=['everyone'],
            writers=[venue_id],
            signatures=[venue_id],
            reply={
                'signatures': { 'values-regex': f'{paper_group.id}/AnonReviewer.*|{paper_group.id}/AEs' },
                'readers': { 'values': [ venue_id, '${signatures}', f'{paper_group.id}/AEs']},
                'writers': { 'values': [ venue_id, '${signatures}', f'{paper_group.id}/AEs']},
                'note': {
                    'forum': { 'value': note.id },
                    'replyto': { 'value': note.id },
                    'signatures': { 'values': ['${signatures}'] },
                    'readers': { 'values': [ venue_id, '${signatures}', f'{paper_group.id}/AEs']},
                    'writers': { 'values': [ venue_id, '${signatures}', f'{paper_group.id}/AEs']},
                    'content': {
                        'title': {
                            'value': {
                                'order': 1,
                                'value-regex': '.{0,500}',
                                'description': 'Brief summary of your review.',
                                'required': True
                            }
                        },
                        'review': {
                            'value': {
                                'order': 2,
                                'value-regex': '[\\S\\s]{1,200000}',
                                'description': 'Please provide an evaluation of the quality, clarity, originality and significance of this work, including a list of its pros and cons (max 200000 characters). Add formatting using Markdown and formulas using LaTeX. For more information see https://openreview.net/faq',
                                'required': True,
                                'markdown': True
                            }
                        },
                        'rating': {
                            'value': {
                                'order': 3,
                                'value-dropdown': [
                                    '10: Top 5% of accepted papers, seminal paper',
                                    '9: Top 15% of accepted papers, strong accept',
                                    '8: Top 50% of accepted papers, clear accept',
                                    '7: Good paper, accept',
                                    '6: Marginally above acceptance threshold',
                                    '5: Marginally below acceptance threshold',
                                    '4: Ok but not good enough - rejection',
                                    '3: Clear rejection',
                                    '2: Strong rejection',
                                    '1: Trivial or wrong'
                                ],
                                'required': True
                            }
                        },
                        'confidence': {
                            'value': {
                                'order': 4,
                                'value-radio': [
                                    '5: The reviewer is absolutely certain that the evaluation is correct and very familiar with the relevant literature',
                                    '4: The reviewer is confident but not absolutely certain that the evaluation is correct',
                                    '3: The reviewer is fairly confident that the evaluation is correct',
                                    '2: The reviewer is willing to defend the evaluation, but it is quite likely that the reviewer did not understand central parts of the paper',
                                    '1: The reviewer\'s evaluation is an educated guess'
                                ],
                                'required': True
                            }
                        }
                    }
                }
            }
    ))

    revision_invitation_id=f'{paper_group.id}/-/Revision'
    invitation = client.post_invitation_edit(readers=[venue_id],
        writers=[venue_id],
        signatures=[venue_id],
        invitation=openreview.Invitation(id=revision_invitation_id,
            invitees=[f"{paper_group.id}/Authors"],
            readers=['everyone'],
            writers=[venue_id],
            signatures=[venue_id],
            reply={
                'referent': { 'value': note.id },
                'signatures': { 'values': [f'{paper_group.id}/Authors'] },
                'readers': { 'values': [ venue_id, '${signatures}', f'{paper_group.id}/AEs', f'{paper_group.id}/Authors']},
                'writers': { 'values': [ venue_id, '${signatures}', f'{paper_group.id}/Authors']},
                'note': {
                    'forum': { 'value': note.id },
                    'content': {
                        'title': {
                            'value': {
                                'description': 'Title of paper. Add TeX formulas using the following formats: $In-line Formula$ or $$Block Formula$$',
                                'order': 1,
                                'value-regex': '.{1,250}',
                                'required':False
                            }
                        },
                        'abstract': {
                            'value': {
                                'description': 'Abstract of paper. Add TeX formulas using the following formats: $In-line Formula$ or $$Block Formula$$',
                                'order': 4,
                                'value-regex': '[\\S\\s]{1,5000}',
                                'required':False
                            }
                        },
                        'authors': {
                            'value': {
                                'description': 'Comma separated list of author names.',
                                'order': 2,
                                'values-regex': '[^;,\\n]+(,[^,\\n]+)*',
                                'required':False,
                                'hidden': True
                            },
                            'readers': {
                                'values': [ venue_id, '${signatures}', f'{paper_group.id}/Authors']
                            }
                        },
                        'authorids': {
                            'value': {
                                'description': 'Search author profile by first, middle and last name or email address. If the profile is not found, you can add the author completing first, middle, last and name and author email address.',
                                'order': 3,
                                'values-regex': r'~.*|([a-z0-9_\-\.]{1,}@[a-z0-9_\-\.]{2,}\.[a-z]{2,},){0,}([a-z0-9_\-\.]{1,}@[a-z0-9_\-\.]{2,}\.[a-z]{2,})',
                                'required':False
                            },
                            'readers': {
                                'values': [ venue_id, '${signatures}', f'{paper_group.id}/Authors']
                            }
                        },
                        'pdf': {
                            'value': {
                                'description': 'Upload a PDF file that ends with .pdf',
                                'order': 5,
                                'value-file': {
                                    'fileTypes': ['pdf'],
                                    'size': 50
                                },
                                'required':False
                            }
                        },
                        "supplementary_material": {
                            'value': {
                                "description": "All supplementary material must be self-contained and zipped into a single file. Note that supplementary material will be visible to reviewers and the public throughout and after the review period, and ensure all material is anonymized. The maximum file size is 100MB.",
                                "order": 6,
                                "value-file": {
                                    "fileTypes": [
                                        "zip",
                                        "pdf"
                                    ],
                                    "size": 100
                                },
                                "required": False
                            },
                            'readers': {
                                'values': [ venue_id, '${signatures}', f'{paper_group.id}/AEs', f'{paper_group.id}/Reviewers', f'{paper_group.id}/Authors' ]
                            }
                        }
                    }
                }
            }))


