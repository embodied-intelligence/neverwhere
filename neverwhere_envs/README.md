# Neverwhere Envs

## Env List

#### Environments with Polycam Scans

1. building_31_stairs_v1
2. curb_gas_tank_v1
3. gaps_12in_226_blue_carpet_v2
4. gaps_16in_226_blue_carpet_v2
5. gaps_226_blue_carpet_v4
6. gaps_fire_outlet_v3
7. gaps_grassy_courtyard_v2
8. gaps_stata_v1
9. hurdle_226_blue_carpet_v3
10. hurdle_black_stone_v1
11. hurdle_one_blue_carpet_v2
12. hurdle_one_dark_grassy_courtyard_v1
13. hurdle_one_light_grassy_courtyard_v1
14. hurdle_one_light_grassy_courtyard_v3
15. hurdle_stata_one_v1
16. hurdle_stata_v1
17. hurdle_stata_v2
18. hurdle_three_grassy_courtyard_v2
19. ramp_aligned_blue_carpet_v4
20. ramp_aligned_covered_blue_carpet_v6
21. ramp_bricks_v2
22. ramp_grass_v1
23. ramp_grass_v3
24. ramp_spread_blue_carpet_v5
25. ramp_spread_covered_blue_carpet_v7
26. real_hurdle_one_blue_carpet_v2
27. real_hurdle_three_grassy_ally_v2
28. real_stair_02_bcs_v1
29. real_stair_03_bcs_golden
30. real_stair_04_bcs_dusk
31. real_stair_07_54_v1
32. real_stair_08_mc_afternoon_v1
33. stairs_36_backstairs_v2
34. stairs_48_v3
35. stairs_4_stairs2up_v1
36. stairs_54_wooden_v1
37. stairs_backstairs_v5
38. stairs_banana_v1
39. stata_ramped_platform_v3
40. wood_ramp_aligned_bricks_v1
41. wood_ramp_aligned_grass_v2
42. wood_ramp_offset_bricks_v2
43. wood_ramp_offset_grass_v1

#### Environments without Polycam Scans

1. _archive
2. gap-stata_v1
3. mesh_camera_left
4. mesh_camera_right
5. real_curb_01
6. real_curb_02
7. real_flat_01_stata_grass
8. real_flat_02_wh_evening
9. real_flat_03_stata_indoor
10. real_gap_01
11. real_gap_02
12. real_hurdle_01
13. real_parkour_01
14. real_stair_01
15. real_stair_05_bcs_rain_v1
16. real_stair_06_wh_evening_v1
17. real_stair_10_wh_afternoon_v1
18. stairs_cf_night_v13
19. stairs_mc_afternoon_v2
20. stairs_wh_evening_v2

## File Structure

Each environment typically follows this file structure:

```
pathtoenvs/
    ├── scene000_name/
    │   ├── environment_name.xml
    │   ├── meshes/
    │   ├── model.ckpt
    │   ├── polycam/
    │   └── transforms/
    ├── scene001_name/
    │   ├── environment_name.xml
    │   ├── meshes/
    │   ├── model.ckpt
    │   ├── polycam/
    │   └── transforms/
    └── ...
```

### Description of files and directories:

1. `environment_name.xml`: XML file containing environment configuration.
2. `meshes/`: Directory containing mesh files and `.spalt` for the environment.
3. `model.ckpt`: 3DGS Checkpoint file.
4. `polycam/`: Directory containing Polycam raw data (may be absent in some environments).
5. `transforms/`: Directory containing `gsplat<->mesh` transformation data

Note: Some environments may have variations in this structure, particularly those listed as not having Polycam scans.