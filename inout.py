''' input/output module '''


def readmesh(mesh_file):
    ''' read HDF5 or DOLFIN XML mesh '''
    # TODO: exceptions, files exist?
    from dolfin import Mesh, MeshFunction, CellFunction, HDF5File, \
        FacetFunction
    # pth = '/'.join(mesh_file.split('/')[0:-1])
    tmp = mesh_file.split('.')  # [-1].split('.')
    mesh_type = tmp[-1]
    mesh_pref = '.'.join(tmp[0:-1])

    if mesh_type == 'xml':
        mesh = Mesh(mesh_file)
        rank = mesh.mpi_comm().Get_rank()
        try:
            subdomains = MeshFunction("size_t", mesh,
                                      mesh_pref+"_physical_region.xml")
        except:
            # if rank == 0:
            #     print('no subdomain file found (%s)' %
            #           (mesh_pref+"_physical_region.xml"))
            subdomains = CellFunction("size_t", mesh)
        try:
            boundaries = MeshFunction("size_t", mesh,
                                      mesh_pref+"_facet_region.xml")
        except:
            if rank == 0:
                print('no boundary file found (%s)' %
                      (mesh_pref+"_facet_region.xml"))
            boundaries = FacetFunction("size_t", mesh)

    elif mesh_type == 'h5':
        mesh = Mesh()
        rank = mesh.mpi_comm().Get_rank()
        hdf = HDF5File(mesh.mpi_comm(), mesh_file, "r")
        hdf.read(mesh, "/mesh", False)
        subdomains = CellFunction("size_t", mesh)
        boundaries = FacetFunction("size_t", mesh)
        if hdf.has_dataset('subdomains'):
            hdf.read(subdomains, "/subdomains")
        else:
            if rank == 0:
                print('no <subdomains> datasets found in file %s' %
                      mesh_file)
        if hdf.has_dataset('boundaries'):
            hdf.read(boundaries, "/boundaries")
        # else:
        #     if rank == 0:
        #         print('no <boundaries> datasets found in file %s' %
        #               mesh_file)

    elif mesh_type in ['xdmf', 'xmf']:
        import sys
        sys.exit('XDMF not supported yet. Use HDF5 instead!')
    else:
        import sys
        sys.exit('mesh format not recognized. try XML (serial) or HDF5')

# NOTE http://fenicsproject.org/qa/5337/importing-marked-mesh-for-parallel-use
    # see file xml2xdmf.py
    return mesh, subdomains, boundaries


def prms_load(infile):
    import yaml
    try:
        with open(infile, 'r+') as f:
            prms = yaml.load(f)
            f.close()
    except IOError:
        import sys
        sys.exit('error: file not found: %s' % infile)
    return prms


def prms_print(prms):
    print("Output")
    for key, val in prms['io'].items():
        print("\t%s: %s" % (key, str(val)))
    print("Numerics")
    for key, val in prms['num'].items():
        print("\t%s: %s" % (key, str(val)))
    """ TODO: run every header only if exist
    print("Physics")
    for key, val in prms['phys'].items():
        print("\t%s: %s" % (key, str(val)))
    """
