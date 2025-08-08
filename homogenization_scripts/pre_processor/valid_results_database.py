# System packages


valid_results_database_file_scheme = { # type: ignore
    'general_settings':{
        'required': True,
        'type': 'dict',
        'schema': {
            'grid_file': {
                'required': True,
                'type': 'string',
            },
            'material_properties': {
                'required': True,
                'type': 'string',
            },
            # 'grain_orientation': {
            #     'required': True,
            #     'type': 'string',
            # },
            'stress_tensor_type':{
                'required': True,
                'type': 'string',
            },
            'strain_tensor_type':{
                'required': True,
                'type': 'string',
            }
        },
    },

    'yield_point':{
        'required': False,
        'type': 'dict',
        'schema': {
            'yield_condition': {
                'required': True,
                'type': 'string',
                'allowed': ["stress_strain_curve", "modulus_degradation","plastic_work"],
            },
            'yield_condition_value': {
                'required': True,
                'type': 'number',
            },
            'N_increments': {
                'required': True,
                'type': 'number',
            },
            'estimated_tensile_yield': {
                'required': True,
                'type': 'number',
            },
            'estimated_shear_yield': {
                'required': True,
                'type': 'number',
            },
            'x-x': {
                'required': False,
                'type': 'list',
                'valuesrules': {'type': 'number'},
            },
            'y-y': {
                'required': False,
                'type': 'list',
                'valuesrules': {'type': 'number'},
            },
            'z-z': {
                'required': False,
                'type': 'list',
                'valuesrules': {'type': 'number'},
            },
            'x-y': {
                'required': False,
                'type': 'list',
                'valuesrules': {'type': 'number'},
            },
            'x-z': {
                'required': False,
                'type': 'list',
                'valuesrules': {'type': 'number'},
            },
            'y-z': {
                'required': False,
                'type': 'list',
                'valuesrules': {'type': 'number'},
            },
        },
    },

    'yield_surface':{
        'required': False,
        'type': 'dict',
        'schema': {
            'stress_state_creation': {
                'required': True,
                'type': 'string',
                'allowed': ["manual", "automatic"],
            },
            'yield_condition': {
                'required': True,
                'type': 'string',
                'allowed': ["stress_strain_curve", "modulus_degradation","plastic_work"],
            },
            'yield_condition_value': {
                'required': True,
                'type': 'number',
            },
            'N_increments': {
                'required': True,
                'type': 'number',
            },
            'estimated_tensile_yield': {
                'required': True,
                'type': 'number',
            },
            'estimated_shear_yield': {
                'required': True,
                'type': 'number',
            },
            'points_per_quadrant': {
                'required': True,
                'type': 'number',
            },
            'results': {
                'required': False,
                'type': 'dict',
                'keysrules': {"type": "string"},
                'valuesrules': {'type': 'dict'},
            }
        },
    },

    'elastic_tensor':{
        'required': False,
        'type': 'dict',
        'schema': {
            'strain_step': {
                'required': True,
                'type': 'number',
            },
        },
    },
}