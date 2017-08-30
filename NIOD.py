
raw_state_data = [
    [ 'AL',  1, 'Alabama'                        ],
    [ 'AK',  2, 'Alaska'                         ],
    [ 'AS', 80, 'American Samoa'                 ],
    [ 'AZ',  3, 'Arizona'                        ],
    [ 'AR',  4, 'Arkansas'                       ],
    [ 'CA',  6, 'California'                     ],
    [ 'CO',  8, 'Colorado'                       ],
    [ 'CT',  9, 'Connecticut'                    ],
    [ 'DE', 10, 'Delaware'                       ],
    [ 'DC', 11, 'District of Columbia'           ],
    [ 'FL', 12, 'Florida'                        ],
    [ 'FM', 64, 'Federated States of Micronesia' ],
    [ 'GA', 13, 'Georgia'                        ],
    [ 'GU', 66, 'Guam'                           ],
    [ 'HI', 15, 'Hawaii'                         ],
    [ 'ID', 16, 'Idaho'                          ],
    [ 'IL', 17, 'Illinois'                       ],
    [ 'IN', 18, 'Indiana'                        ],
    [ 'IA', 19, 'Iowa'                           ],
    [ 'KS', 20, 'Kansas'                         ],
    [ 'KY', 21, 'Kentucky'                       ],
    [ 'LA', 22, 'Louisiana'                      ],
    [ 'ME', 23, 'Maine'                          ],
    [ 'MH', 68, 'Marshall Islands'               ],
    [ 'MD', 24, 'Maryland'                       ],
    [ 'MA', 25, 'Massachusetts'                  ],
    [ 'MI', 26, 'Michigan'                       ],
    [ 'MN', 27, 'Minnesota'                      ],
    [ 'MS', 28, 'Mississippi'                    ],
    [ 'MO', 29, 'Missouri'                       ],
    [ 'MT', 30, 'Montana'                        ],
    [ 'NE', 31, 'Nebraska'                       ],
    [ 'NV', 32, 'Nevada'                         ],
    [ 'NH', 33, 'New Hampshire'                  ],
    [ 'NJ', 34, 'New Jersey'                     ],
    [ 'NM', 35, 'New Mexico'                     ],
    [ 'NY', 36, 'New York'                       ],
    [ 'NC', 37, 'North Carolina'                 ],
    [ 'ND', 38, 'North Dakota'                   ],
    [ 'MP', 69, 'Northern Mariana Islands'       ],
    [ 'OH', 39, 'Ohio'                           ],
    [ 'OK', 40, 'Oklahoma'                       ],
    [ 'OR', 41, 'Oregon'                         ],
    [ 'PW', 70, 'Palau'                          ],
    [ 'PA', 42, 'Pennsylvania'                   ],
    [ 'PR', 72, 'Puerto Rico'                    ],
    [ 'RI', 44, 'Rhode Island'                   ],
    [ 'SC', 45, 'South Carolina'                 ],
    [ 'SD', 46, 'South Dakota'                   ],
    [ 'TN', 47, 'Tennessee'                      ],
    [ 'TX', 48, 'Texas'                          ],
    [ 'UM', 74, 'U.S. Minor Outlying Islands'    ],
    [ 'UT', 49, 'Utah'                           ],
    [ 'VT', 50, 'Vermont'                        ],
    [ 'VA', 51, 'Virginia'                       ],
    [ 'VI', 78, 'U.S. Virgin Islands'            ],
    [ 'WA', 53, 'Washington'                     ],
    [ 'WV', 54, 'West Virginia'                  ],
    [ 'WI', 55, 'Wisconsin'                      ],
    [ 'WY', 56, 'Wyoming'                        ],
]

class State(object):
    def __init__(self, data):
        self.long_name = data[2]
        self.short_name = data[0]
        self.fips = data[1]

    def get_name(self):
        return self.long_name

    def get_abbrev(self):
        return self.short_name

    def get_fips(self):
        return self.fips

    @staticmethod
    def get_all():
        sts = []
        for t in raw_state_data:
            st = State(t)
            sts.append(st)

        return sts
    
    @staticmethod
    def find_by_name(name):
        st = None
        for t in raw_state_data:
            if t[2].upper() == name.upper():
                st = State(t)

        return st

    @staticmethod
    def find_by_abbrev(abbrev):
        st = None
        for t in raw_state_data:
            if t[0] == abbrev.upper():
                st = State(t)

        return st

    @staticmethod
    def find_by_fips(fips):
        st = None
        for t in raw_state_data:
            if t[1] == fips:
                st = State(t)

        return st

class Report(object):
    def __init__(self, id):
        self.id = id

class FederalAudit(Report):
    def __init__(self, id):
        self.id = id

    def get_id(self):
        return self.id
