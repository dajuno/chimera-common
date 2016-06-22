def create_rectangle_mesh(prms):
  # =========================================
  # briefly generate domain to solve homogenized problem
  domain_h = ASD.Rectangle(Point(0., 0.), Point(base + b*desp, altura + 2*a*desp))
  class Left(SubDomain):
      def inside(self, x, on_boundary):
	  return near(x[0], 0.0)
  class Right(SubDomain):
      def inside(self, x, on_boundary):
	  return near(x[0], basse)
  class Bottom(SubDomain):
      def inside(self, x, on_boundary):
	  return near(x[1], 0.0)
  class Top(SubDomain):
      def inside(self, x, on_boundary):
	  return near(x[1], altura)
  # TODO: write boundaries to file
  res = 1
  mesh_h = ASD.generate_mesh(domain, res)
  plot(mesh_h)
  interactive()	
  # =========================================