chassis_length = 10;
chassis_width = 10;
chassis_height = 5;
//define chassis variable
chassis_dim = [chassis_length, chassis_width, chassis_height
];
frame_width = 1;
axle_position = 3;
axle_diameter = 0.5;
shelf_height = 2;
clearance = 0.2;
$fn = 60;

union(){
    difference() {
        //outer structure
        cube(chassis_dim, center = true);
        
        
        
        //cutout on x axis
        cube([
            chassis_dim[0] + clearance,
            chassis_dim[1] - (2 * frame_width),
            chassis_dim[2] - (2 * frame_width)
        ], center = true);
        
        
        
        //cutout on y axis
        cube([
            chassis_dim[0] - (2 * frame_width),
            chassis_dim[1] + clearance,
            chassis_dim[2] - (2 * frame_width)
        ], center = true);
        
        
        
        //cutout on z axis
        cube([
            chassis_dim[0] - (2 * frame_width),
            chassis_dim[1] - (2 * frame_width),
            chassis_dim[2] + clearance
        ], center = true);
        
        //move cylindar
        translate([
            (chassis_dim[0] / 2) - axle_position, 
            0,
            ((frame_width / 2) - (chassis_dim[2] / 2))
            ]){
                
                //rotate cylinder
            rotate([90, 0, 0]) {
            
                //create cylinder for axle
                cylinder(h = chassis_dim[0] + clearance, r = (axle_diameter/2), center = true);
            
            }
        }
    }
    
    
    translate([
    -chassis_dim[0] / 4,
    0,
    (chassis_dim[2] / 2) - ((chassis_dim[2] - shelf_height) / 2)
    ]){
        
        difference(){
            
            //create outer
            cube([
            chassis_dim[0] / 2,
            chassis_dim[1],
            (chassis_dim[2] - shelf_height)
        ], center = true);
            
            
            //move cut out
            translate([
            
                frame_width / 4,
                0,
                0.75
            
            ]){
                //create cut out
                cube([
                    ((chassis_dim[0] / 2) - frame_width) - 0.5,
                    chassis_dim[1] - (2 * frame_width),
                    chassis_dim[2] - shelf_height
                ], center = true);
            }
        }
        
    }
    
}
    