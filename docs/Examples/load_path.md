# Simple loading and unloading case

In this example, a loading and unloading case will be simulated using DAMASK. First, a load is applied in the `x-y` shear direction, then a normal `x-x` direction after which the material is unloaded. The resulting stress and strain at every increment will be the output data.

It will be assumed that the user provides a ready-to-use grid file (`grid.vti`) and material properties file (`material_properties.yaml`).

The overall steps will be:

- Creating a project and adding the settings
- Running the simulation
- Finding the results

## Creating the project

In this example, the project name is assumed to be `loading_unloading`, the grid file to be located in the project folder as `input_files/grid.vti` and the material properties file in the project folder as `input_files/material_properties.yaml`. In this example the randomly grid and material properties files are used from the ExampleProject, with the estimated yield strengths found in the [`uniaxial yield points`](yield_point.md) example.

Within the project folder, create the `problem_definition.yaml`. Add the following configuration:

```
general: 
    simulation_type     : load_path
    remove_damask_files_after_job_completion: True
    dimensions          : 3D
    material_properties : "input_files/material_properties.yaml"
    grid_file           : "input_files/grid.vti"
    stress_tensor_type: "Cauchy"
    strain_tensor_type: "true_strain"
    reduce_parasitic_stresses : False

yielding_condition:
    # These are not relevant for this simulation but have to be present
    yield_condition: stress_strain_curve
    plastic_strain_yield: 0.002
    modulus_degradation_percentage: 0.15
    estimated_tensile_yield: 650e6
    estimated_shear_yield: 350e6

solver:
    N_increments: 15
    cpu_cores: 0
    # The following settings are technical DAMASK settings
    stop_after_subsequent_parsing_errors: 20
    solver_type: "spectral_basic"
    N_staggered_iter_max: 10      
    N_cutback_max: 3        
    N_iter_min: 1            
    N_iter_max: 100         
    eps_abs_div_P: 1.0e-4            
    eps_rel_div_P: 5.0e-4            
    eps_abs_P: 1.0e3                  
    eps_rel_P: 1.0e-3                 
    eps_abs_curl_F: 1.0e-10          
    eps_rel_curl_F: 5.0e-4           

    simulation_time : 1000         
    monitor_update_cycle: 5 

load_path:
    # Example loading with steps: unloaded -> loading xy -> loading xx -> unloaded
    stress_x_x: [    0, 600e6, 0] 
    stress_x_y: [250e6,     0, 0]
    stress_x_z: [    0,     0, 0]
    stress_y_y: [    0,     0, 0]
    stress_y_z: [    0,     0, 0]
    stress_z_z: [    0,     0, 0]

    enable_yield_detection: False
```

In this configuration the following important settings for this simulation are found:

The simulation type is set for the elasticity properties:

- `simulation_type`     : load_path

The simulation will have 45 increments in total, 15 per applied stress state for 3 stress states:

- `N_increments`: 15

For the first stress state, the normal xx direction is unloaded, then it is loaded and finally it is unloaded again:

- `stress_x_x`: [0, 600e6, 0]

For the first stress state, the shear xy direction is loaded, then it is unloaded for the next two states:

- `stress_x_y`: [0, 600e6, 0]

All other directions remain unloaded of the rest of the test:

- `stress_`: [0, 0, 0]

The simulation will not stop when yielding is detected:

- `enable_yield_detection`: False
  
  `Note:` This yield detection is only properly defined for the first stress state, for the stress states after the first the yielding definitions and/or application breaks and yielding might be detected when it should or shouldn't be.

This concludes setting up the simulation details.

## Running the simulations

With the project folder created, the grid and materials added and problem definition defined, the project can be run. Go to installation root and run the project. Do not forget to activate a Conda environment if needed.

```
# Activate Conda environment if needed:
conda activate [environment_name]

# Run the project
python run_project.py loading_unloading
```

This should end up in a summary of the simulations to run. 

Check if the settings match what was expected and confirm.

## The simulation is completed

When the simulations are completed, the results will be stored in the results folder inside of the project folder.

Unlike the other simulation types, the load path results are found in the `load_path` folder and then inside of a `load_path` folder including the date and time of when the simulation was run. For example, the results could be found in a folder similar to `results/load_path/load_path_2024-11-19_13-21-51/`. 

In this folder, the `load_path_results.csv` file can be found, this contains the homogenized stress and strain data on each increment. For this simulation, the contents of this file look similar to:

```
increment,stress_xx,stress_yy,stress_zz,stress_yz,stress_xz,stress_xy,strain_xx,strain_yy,strain_zz,strain_yz,strain_xz,strain_xy
0,[-1.5684328e-05],[-1.99684232e-05],[-1.85399078e-05],[-2.69367796e-07],[6.5920516e-07],[9.02677384e-07],[0.],[0.],[0.],[0.],[0.],[0.]
1,[6454.70236969],[-26.51146066],[2.53169889],[-22.0292308],[9.95149619],[16666691.42543323],[1.72485371e-06],[1.19356015e-06],[-3.20911332e-06],[6.61727719e-07],[4.65427755e-06],[0.00038207]
2,[25526.17268025],[75.53403812],[-392.4631324],[-284.92004014],[18.06054885],[33333833.87422508],[3.41489747e-06],[2.20564846e-06],[-6.39079344e-06],[1.31475563e-06],[9.3101094e-06],[0.00076416]
3,[57029.58839819],[-281.39715809],[-117.4638025],[151.43571451],[-22.65132235],[49999809.45198557],[5.06648752e-06],[3.02771238e-06],[-9.5322106e-06],[1.98415571e-06],[1.39569312e-05],[0.00114618]
4,[102901.45498843],[888.63526801],[490.42181441],[34.37211221],[-199.20975876],[66667292.54897515],[6.6931934e-06],[3.67435048e-06],[-1.26500243e-05],[2.6357895e-06],[1.86047366e-05],[0.00152826]
5,[160954.9950379],[1651.12837719],[701.75103925],[-3.88671462],[83.52071344],[83333962.10631076],[8.28221165e-06],[4.13485033e-06],[-1.57360642e-05],[3.28727343e-06],[2.32598759e-05],[0.0019103]
6,[228499.72209646],[-1451.15471437],[-807.29179465],[47.87721031],[-27.96427733],[1.00000056e+08],[9.80814409e-06],[4.40600006e-06],[-1.87846534e-05],[3.95455074e-06],[2.79128799e-05],[0.00229244]
7,[310927.24708616],[-692.45141878],[-420.47576507],[-232.39997295],[889.55727712],[1.16674129e+08],[1.11065885e-05],[4.78259874e-06],[-2.18731577e-05],[4.59107078e-06],[3.32042264e-05],[0.0026802]
8,[413097.38133956],[-1.9008888],[-38.72518068],[2.11914218],[-112.78348461],[1.33335363e+08],[1.21053113e-05],[6.18736165e-06],[-2.5847367e-05],[3.26122505e-06],[4.1986695e-05],[0.00310015]
9,[536815.90606683],[-139.79710584],[-354.57437337],[112.92912589],[-1348.67400891],[1.50002706e+08],[1.30893925e-05],[9.66292937e-06],[-3.20516416e-05],[-5.24481845e-06],[5.69131331e-05],[0.00358364]
10,[688314.12290881],[373.44197847],[0.804141],[-95.32048769],[-130.05542686],[1.66670924e+08],[1.48450608e-05],[1.47192376e-05],[-4.07995747e-05],[-2.32674027e-05],[7.93840917e-05],[0.0041319]
11,[869125.32436536],[476.08750033],[-55.11562748],[-356.07050994],[-16.94345998],[1.8334012e+08],[1.881091e-05],[2.18211784e-05],[-5.40244976e-05],[-4.8921025e-05],[0.00011018],[0.00474198]
12,[1086207.97444661],[5.28322471],[452.86947668],[-173.73362759],[52.93530995],[2.0001043e+08],[2.65907371e-05],[3.32492943e-05],[-7.56031069e-05],[-8.03158074e-05],[0.00014641],[0.00543123]
13,[1355365.60409029],[-170.0162064],[596.8304554],[-591.26862347],[337.84335315],[2.16682367e+08],[4.04112435e-05],[5.12725124e-05],[-0.00011001],[-0.00011507],[0.0001845],[0.00625444]
14,[1703231.60613876],[-408.29676885],[501.22687752],[-298.8701509],[-82.98481587],[2.33357798e+08],[6.20656832e-05],[7.68650373e-05],[-0.00015998],[-0.00015411],[0.0002222],[0.00730067]
15,[2171922.11570936],[83.94078469],[327.56602804],[-347.90015111],[-131.09966005],[2.50036651e+08],[9.43065389e-05],[0.00010954],[-0.00022769],[-0.00020089],[0.00025894],[0.00868696]
16,[42006213.35359614],[-2090.5397107],[-2348.99856418],[136.45110483],[92.49864925],[2.33306602e+08],[0.00047346],[-1.4845671e-05],[-0.00035508],[-0.00022619],[0.00026134],[0.00852739]
17,[81835315.12883034],[1373.9565935],[2034.10574834],[1027.76103868],[-712.76713699],[2.16587396e+08],[0.000839],[-0.00013735],[-0.000471],[-0.00024522],[0.00026158],[0.00823776]
18,[1.2169252e+08],[2969.11580868],[2890.08914606],[159.72378895],[356.67194485],[1.99878817e+08],[0.00119955],[-0.00025816],[-0.00058417],[-0.00026428],[0.00026146],[0.00791322]
19,[1.61560129e+08],[-397.66452366],[-842.70351995],[102.03537865],[379.84724044],[1.83178577e+08],[0.00155997],[-0.00037928],[-0.00069752],[-0.00028491],[0.00026118],[0.00757857]
20,[2.01469015e+08],[1189.94191986],[526.41158853],[435.01714708],[2.08889918],[1.66484247e+08],[0.0019265],[-0.00050425],[-0.00081359],[-0.00030796],[0.00026092],[0.00724202]
21,[2.4141647e+08],[-2311.53298787],[-1866.88615576],[-911.01048235],[117.71418264],[1.49795194e+08],[0.00231665],[-0.00064571],[-0.00093728],[-0.00033794],[0.00026145],[0.00690667]
22,[2.81407665e+08],[-408.80253638],[-45.15552789],[96.0373978],[-340.26499144],[1.33111355e+08],[0.00275587],[-0.00082124],[-0.00107635],[-0.00038309],[0.00026352],[0.00657489]
23,[3.21457092e+08],[-1268.80972082],[154.42371107],[-6.07731828],[-216.67374109],[1.16433237e+08],[0.00325887],[-0.00103728],[-0.00123915],[-0.00044735],[0.00026628],[0.00625326]
24,[3.61578779e+08],[537.96468653],[-120.82746944],[-70.39849445],[542.07508364],[99760891.36330369],[0.00384157],[-0.0013009],[-0.00143452],[-0.00053587],[0.00026538],[0.00594891]
25,[4.01792889e+08],[1223.48513083],[-161.32342319],[-472.67728684],[743.09080159],[83096557.68118976],[0.00453485],[-0.00162981],[-0.00167557],[-0.00065433],[0.0002535],[0.00566503]
26,[4.42142564e+08],[979.02836094],[89.50139897],[513.11693427],[121.34520634],[66440536.54156943],[0.00539671],[-0.00206045],[-0.00198376],[-0.00080956],[0.00023037],[0.00540164]
27,[4.82680474e+08],[-1054.5715172],[-157.92901559],[-124.58559961],[-22.62993265],[49795505.7524977],[0.00651476],[-0.0026466],[-0.00239285],[-0.00101439],[0.00020355],[0.00516141]
28,[5.23511394e+08],[2182.23678192],[474.21696202],[409.26894987],[185.69862927],[33166345.85072992],[0.00801637],[-0.00346233],[-0.00295587],[-0.00130088],[0.00017559],[0.00495067]
29,[5.64814174e+08],[-1588.32220234],[-2044.27620368],[143.71697096],[7.45993019],[16561100.97268797],[0.01015147],[-0.00465705],[-0.00377281],[-0.00173305],[0.00014786],[0.0047454]
30,[6.06973914e+08],[-2320.58666305],[-3066.87712066],[461.98845601],[-55.16955614],[-746.8732192],[0.01341486],[-0.0065221],[-0.00504524],[-0.00241719],[0.00014689],[0.00447376]
31,[5.66686119e+08],[-24887.74555087],[-17816.96684656],[-3072.35562447],[887.74007114],[-914.21976538],[0.01361056],[-0.00672847],[-0.00515933],[-0.00252168],[0.00016268],[0.00450806]
32,[5.26008995e+08],[79691.62473469],[59842.91012174],[10995.22829773],[2156.74662138],[-1729.00806173],[0.01337301],[-0.0066749],[-0.00509644],[-0.00253007],[0.0001709],[0.00451224]
33,[4.8558889e+08],[594.53268262],[-1191.20912329],[-1275.20365274],[801.25528444],[-509.84142154],[0.01306016],[-0.00657736],[-0.0050029],[-0.00252486],[0.00017375],[0.00451001]
34,[4.45027164e+08],[1718.51847087],[1711.34771155],[-4129.54667071],[3391.32378414],[-2.0353285],[0.01273133],[-0.00647073],[-0.0049029],[-0.00251758],[0.00017402],[0.00450597]
35,[4.04485325e+08],[-2573.30981781],[4619.68026914],[-1891.77693039],[-2716.35301708],[-2155.97401109],[0.01239818],[-0.00636205],[-0.00480102],[-0.00251037],[0.00017292],[0.00450139]
36,[3.63961205e+08],[-3229.36644755],[7.00182888],[-2064.79646088],[-582.36140406],[4071.07148748],[0.01206363],[-0.0062525],[-0.00469899],[-0.00250267],[0.00017137],[0.0044964]
37,[3.23457793e+08],[-636.65146072],[-2757.47132828],[1735.8503044],[-1078.31061815],[370.08007455],[0.01172839],[-0.00614277],[-0.0045968],[-0.00249501],[0.00016961],[0.00449103]
38,[2.82960605e+08],[-662.71147309],[-5156.55857821],[3313.14811992],[-878.02373218],[-1297.952609],[0.01139241],[-0.00603289],[-0.00449441],[-0.00248748],[0.00016773],[0.00448554]
39,[2.42481723e+08],[-952.45804184],[-1660.81784502],[494.7500675],[-215.6627363],[-682.36418399],[0.0110558],[-0.00592291],[-0.00439183],[-0.00248009],[0.00016578],[0.0044799]
40,[2.02025016e+08],[-1038.4222062],[-537.25698996],[-510.63196403],[-143.91410679],[196.81232791],[0.01071854],[-0.00581279],[-0.00428909],[-0.00247272],[0.00016376],[0.00447408]
41,[1.61583641e+08],[-714.82425567],[-681.45437074],[-302.20201864],[-436.74776048],[-431.87913178],[0.01038025],[-0.00570231],[-0.00418604],[-0.00246538],[0.00016164],[0.00446782]
42,[1.21166707e+08],[419.98013899],[607.68631375],[74.3557978],[44.71941663],[-6.93817103],[0.01004019],[-0.00559098],[-0.00408239],[-0.0024581],[0.00015913],[0.00446061]
43,[80759671.7417874],[-119.42275148],[-160.40773252],[213.59451218],[35.37322255],[-0.92475461],[0.00969455],[-0.00547633],[-0.00397682],[-0.00245048],[0.00015525],[0.00445143]
44,[40369939.74631289],[-2.30329609],[12.98200718],[9.68315764],[1.07509158],[-11.02023998],[0.00932857],[-0.00534895],[-0.00386386],[-0.00244074],[0.000149],[0.00444079]
45,[-2.54947905e-05],[-2.56538236e-05],[-2.56046627e-05],[-1.31535286e-08],[1.11206607e-08],[-1.10633205e-08],[0.00892441],[-0.00519874],[-0.00373561],[-0.00242611],[0.00013944],[0.00443148]
```

Also, the stress strain curve can be found, this is located under `results/stress_strain_curve.png`. For this simulation example, the following stress/strain curves have been found:
![Stress strain curves of the loading/unloading case](stress_strain_curve_loading_unloading.png).
