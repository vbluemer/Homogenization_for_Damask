valid_problem_definition_file_scheme = {  # type: ignore
    'general':{
        'required': True,
        'type': 'dict',
        'schema': {
            'simulation_type': {
                'required': True,
                'type': 'string',
                'allowed': ['yield_point', 'yield_surface', 'elastic_tensor', 'load_path'],
            },
            'remove_damask_files_after_job_completion': {
                'required': True,
                'type': 'boolean'
            },
            'dimensions': {
                'required': False,
                'type': 'string',
                'allowed': ['2D', '3D'],
            },
            'reduce_parasitic_stresses': {
                'required': False,
                'type': 'boolean'
            },
            'material_properties': {
                'required': True,
                'type': 'string',
            },
            # 'grain_orientation': {
            #     'required': True,
            #     'type': 'string',
            # },
            'grid_file': {
                'required': True,
                'type': 'string',
            },
            'dimensions_file': {
                'required': False,
                'type': 'string',
            },
            'stress_tensor_type': {
                'required': True,
                'type': 'string',
                'allowed': ['PK1', 'PK2', 'Cauchy'],
            },
            'strain_tensor_type': {
                'required': True,
                'type': 'string',
                'allowed': ['true_strain', 'Green_Lagrange'],
            },
        },
    },

    'yielding_condition':{
        'required': True,
        'type': 'dict',
        'schema': {
            'yield_condition': {
                'required': True,
                'type': 'string',
                'allowed': ["stress_strain_curve", "modulus_degradation","plastic_work"],
            },
            'plastic_strain_yield': {
                'required': True,
                'type': 'number',
            },
            'modulus_degradation_percentage': {
                'required': True,
                'type': 'number',
            },
            'plastic_work_threshold': {
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
        }
    },

    'solver':{
        'required': True,
        'type': 'dict',
        'schema': {
            'N_increments': {
                'required': True,
                'type': 'integer',
            },
            'cpu_cores': {
                'required': True,
                'type': 'integer',
            },
            'stop_after_subsequent_parsing_errors': {
                'required': True,
                'type': 'integer',
            },
            'solver_type': {
                'required': True,
                'type': 'string',
                'allowed': ["spectral_basic", "FEM"],
            },
            'N_staggered_iter_max': {
                'required': True,
                'type': 'integer',
            },
            'N_cutback_max': {
                'required': True,
                'type': 'integer',
            },
            'N_iter_min': {
                'required': True,
                'type': 'integer',
            },
            'N_iter_max': {
                'required': True,
                'type': 'integer',
            },
            'eps_abs_div_P': {
                'required': True,
                'type': 'number',
            },
            'eps_rel_div_P': {
                'required': True,
                'type': 'number',
            },
            'eps_abs_P': {
                'required': True,
                'type': 'number',
            },
            'eps_rel_P': {
                'required': True,
                'type': 'number',
            },
            'eps_abs_curl_F': {
                'required': True,
                'type': 'number',
            },
            'eps_rel_curl_F': {
                'required': True,
                'type': 'number',
            },
            'simulation_time': {
                'required': True,
                'type': 'integer',
            },
            'monitor_update_cycle': {
                'required': True,
                'type': 'float',
            },

        }
    },

    'yield_point':{
        'required': False,
        'type': 'dict',
        'schema': {
            'load_direction': {
                'required': True,
                'type': ['string', 'list'],
                'valuesrules': {'type': 'string'},
                'allowed': ["x-x", "x-y", "x-z", "y-y", "y-z", "z-z"],
            },
        },
    },

    'yield_surface':{
        'required': False,
        'type': 'dict',
        'schema': {
            'yield_criterion': {
                'required': True,
                'type': 'string',
            },
            'load_points_per_quadrant': {
                'required': True,
                'type': 'integer',
            },
            'assume_tensile_compressive_symmetry': {
                'required': True,
                'type': 'boolean',
            },
            'stress_x_x': {
                'required': True,
                'type': ['number', 'list'],
                'valuesrules': {'type': 'number'},
            },
            'stress_x_y': {
                'required': True,
                'type': ['number', 'list'],
                'valuesrules': {'type': 'number'},
            },
            'stress_x_z': {
                'required': True,
                'type': ['number', 'list'],
                'valuesrules': {'type': 'number'},
            },
            'stress_y_y': {
                'required': True,
                'type': ['number', 'list'],
                'valuesrules': {'type': 'number'},
            },
            'stress_y_z': {
                'required': True,
                'type': ['number', 'list'],
                'valuesrules': {'type': 'number'},
            },
            'stress_z_z': {
                'required': True,
                'type': ['number', 'list'],
                'valuesrules': {'type': 'number'},
            },
        },
    },

    'elastic_tensor':{
        'required': False,
        'type': 'dict',
        'schema': {
            'material_type': {
                'required': True,
                'type': 'string',
                'allowed': ["anisotropic",  "monoclinic", "orthotropic", "tetragonal", "cubic", "isotropic"],
            },
            'component_fitting': {
                'required': True,
                'type': 'string',
                'allowed': ["algebraic",  "optimization"],
            },
            'number_of_load_cases': {
                'required': True,
                'type': 'string',
                'allowed': ["minimum",  "all_directions", "combined_directions"],
            },
            'strain_step': {
                'required': True,
                'type': 'number',
            },
        },
    },

    'load_path':{
        'required': False,
        'type': 'dict',
        'schema': {
            'stress_x_x': {
                'required': True,
                'anyof': [
                    {'type': 'number'},                      
                    {'type': 'string', 'allowed': ['x']},     
                    {'type': 'list', 'schema': {              
                        'anyof': [
                            {'type': 'number'},
                            {'type': 'string', 'allowed': ['x']},
                        ]
                    }},
                ],
            },
            'stress_x_y': {
    				'required': True,
    				'anyof': [
    					{'type': 'number'},                      
    					{'type': 'string', 'allowed': ['x']},    
    					{'type': 'list', 'schema': {             
    						'anyof': [
    							{'type': 'number'},
    							{'type': 'string', 'allowed': ['x']},
    						]
    					}},
    				],
            },
            'stress_x_z': {
					'required': True,
					'anyof': [
						{'type': 'number'},                       
						{'type': 'string', 'allowed': ['x']},    
						{'type': 'list', 'schema': {              
							'anyof': [
								{'type': 'number'},
								{'type': 'string', 'allowed': ['x']},
							]
						}},
					],
            },
            'stress_y_y': {
					'required': True,
					'anyof': [
						{'type': 'number'},                       
						{'type': 'string', 'allowed': ['x']},     
						{'type': 'list', 'schema': {              
							'anyof': [
								{'type': 'number'},
								{'type': 'string', 'allowed': ['x']},
							]
						}},
					],            
            },
            'stress_y_z': {
					'required': True,
					'anyof': [
						{'type': 'number'},                       
						{'type': 'string', 'allowed': ['x']},     
						{'type': 'list', 'schema': {              
							'anyof': [
								{'type': 'number'},
								{'type': 'string', 'allowed': ['x']},
							]
						}},
					],
            },
            'stress_z_z': {
					'required': True,
					'anyof': [
						{'type': 'number'},                      
						{'type': 'string', 'allowed': ['x']},     
						{'type': 'list', 'schema': {             
							'anyof': [
								{'type': 'number'},
								{'type': 'string', 'allowed': ['x']},
							]
						}},
					],            
            },
            'F_x_x': {
					'required': True,
					'anyof': [
						{'type': 'number'},                       
						{'type': 'string', 'allowed': ['x']},     
						{'type': 'list', 'schema': {             
							'anyof': [
								{'type': 'number'},
								{'type': 'string', 'allowed': ['x']},
							]
						}},
					],
            },
            'F_x_y': {
					'required': True,
					'anyof': [
						{'type': 'number'},                       
						{'type': 'string', 'allowed': ['x']},     
						{'type': 'list', 'schema': {             
							'anyof': [
								{'type': 'number'},
								{'type': 'string', 'allowed': ['x']},
							]
						}},
					],
            },
            'F_x_z': {
					'required': True,
					'anyof': [
						{'type': 'number'},                       
						{'type': 'string', 'allowed': ['x']},     
						{'type': 'list', 'schema': {              
							'anyof': [
								{'type': 'number'},
								{'type': 'string', 'allowed': ['x']},
							]
						}},
					],
            },
            'F_y_y': {
					'required': True,
					'anyof': [
						{'type': 'number'},                       
						{'type': 'string', 'allowed': ['x']},     
						{'type': 'list', 'schema': {              
							'anyof': [
								{'type': 'number'},
								{'type': 'string', 'allowed': ['x']},
							]
						}},
					],
            },
            'F_y_z': {
					'required': True,
					'anyof': [
						{'type': 'number'},                       
						{'type': 'string', 'allowed': ['x']},     
						{'type': 'list', 'schema': {              
							'anyof': [
								{'type': 'number'},
								{'type': 'string', 'allowed': ['x']},
							]
						}},
					],
            },
            'F_z_z': {
					'required': True,
					'anyof': [
						{'type': 'number'},                       
						{'type': 'string', 'allowed': ['x']},     
						{'type': 'list', 'schema': {              
							'anyof': [
								{'type': 'number'},
								{'type': 'string', 'allowed': ['x']},
							]
						}},
					],
            },
            'unloading': {
                'required': True,
                'type': 'boolean',
            },
            'enable_yield_detection': {
                'required': False,
                'type': 'boolean',
            },
        },
    },
}