def generate_mesh(prms):
    # Generate fibrotic mesh using GMSH
    # The labels are:
    #   collagen subdomains: 5
    #   healthy tissue: 6
    #   left boundary: 4
    #   right boundary: 2
    #   top boundary: 3
    #   bottom boundary: 1
    #
    #	Felipe Galarce Marin - 2016
    #	felipe.galarce.m@gmail.com

    from dolfin import *
    import pygmsh as pg
    import numpy as np
    from functions import utils
    import subprocess


    # Extract parameters
    a 	    = prms['mesh']['a']
    b 	    = prms['mesh']['b']
    theta_c = prms['mesh']['theta_c']
    theta_f = prms['mesh']['theta_f']
    base    = prms['mesh']['base']
    altura  = prms['mesh']['altura']
    desp    = prms['mesh']['desp']

    l_coarse = 0.5
    l_size = (theta_c < theta_f)*theta_c*a + (theta_c >= theta_f)*theta_f*b;
    print "l_size = %g" % l_size
    geom = pg.Geometry()

    X = [[0.0, 0.0, 0.0], [base, 0.0, 0.0], [base, altura, 0.0], [0.0, altura, 0.0]];
    surface_id = geom.add_polygon(X, l_coarse, holes=None)

    # create collagen subdomains
    collagen_subdomain, k = '{', 0
    for Px in range(0, int(np.floor(base/b - desp/theta_f/b) + 1)):
      for Py in range(0, int(np.floor(altura/a - desp/theta_c/a + 1))):
    #for Px in range(0, int(np.floor(base/b - desp + 1))):
      #for Py in range(0, int(np.floor(altura/a - desp/theta_c/a + 1))):

	Px, Py = Px*b, Py*a    
	x1 = [Px + desp,             Py + desp,       0.0];
	x2 = [Px + b*theta_f + desp, Py + desp,        0.0];
	x3 = [Px + b*theta_f + desp, Py + a*theta_c + desp, 0.0];
	x4 = [Px + desp,             Py + a*theta_c + desp, 0.0];

	x1_label = geom.add_point_in_surface(x1, l_size, surface_id);
	x2_label = geom.add_point_in_surface(x2, l_size, surface_id);
	x3_label = geom.add_point_in_surface(x3, l_size, surface_id);
	x4_label = geom.add_point_in_surface(x4, l_size, surface_id);

	l1_label = geom.add_line(x1_label, x2_label);
	l2_label = geom.add_line(x2_label, x3_label);
	l3_label = geom.add_line(x3_label, x4_label);
	l4_label = geom.add_line(x4_label, x1_label);    
	llp      = geom.add_line_loop((l1_label, l2_label, l3_label, l4_label))
	collagen = geom.add_plane_surface(llp)

	if k == 0:
	  collagen_subdomain = collagen_subdomain + collagen
	  k = 1
	else:
	  collagen_subdomain = collagen_subdomain +  ", " + collagen

	l1_label = geom.add_line_in_surface(l1_label, surface_id);
	l2_label = geom.add_line_in_surface(l2_label, surface_id);
	l3_label = geom.add_line_in_surface(l3_label, surface_id);
	l4_label = geom.add_line_in_surface(l4_label, surface_id);
    collagen_subdomain = collagen_subdomain + '}'

    # unrefine place where fine mesh is not required
    l_unrefine = 1 # mesh size in coarser parts of the mesh
    unrefine_points = 0.33*np.array(range(1, int(altura*3)))
    xx = desp + b*(theta_f + 1)/2 - b + b*np.array(range(1, int(base/b)))

    for Py in unrefine_points:
      for Px in xx:
	geom.add_point_in_surface([Px, Py, 0], l_unrefine, surface_id)

    geom.set_physical_objects(collagen_subdomain)

    # TODO: unrefine horizontal lines between laminations (is necessary??)

    out_name = 'fibro_' + str(int(base)) + "x" + str(int(altura)) + "_" + str(int(a*10)) + "_" + str(int(b*10)) + "_" + str(int(theta_c*100)) + "_" + str(int(theta_f*100))
    utils.trymkdir(prms['io']['results'])
    FILE = open("./fibro_file.geo", 'w+')
    FILE.write(geom.get_code()); FILE.close();
    subprocess.call("cp ./functions/geo2h5.sh ./", shell=True)
    subprocess.call("cp ./functions/xml2hdf5.py ./", shell=True)
    subprocess.call("./geo2h5.sh" + " fibro_file " + out_name, shell=True)
    subprocess.call("cp ./" + out_name + ".h5 ./meshes/", shell=True)
    subprocess.call("rm ./geo2h5.sh ./xml2hdf5.py " + out_name + ".h5 fibro_file.geo", shell=True)