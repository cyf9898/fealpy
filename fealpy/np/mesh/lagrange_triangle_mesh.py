from typing import Optional, Union, List,Tuple

import numpy as np
from numpy.typing import NDArray

from .mesh_base import _S
from .lagrange_mesh import LagrangeMesh
from .triangle_mesh import TriangleMesh
from .quadrature import Quadrature

from .. import logger
from . import functional as F
from .mesh_base import HomogeneousMesh, estr2dim

Index = Union[NDArray, int, slice]
_dtype = np.dtype
_S = slice(None)


class LagrangeTriangleMesh(LagrangeMesh):
    def __init__(self, node: NDArray, cell: NDArray, p=1, surface=None,
            construct=False):
        super().__init__(TD=2)

        self.p = p
        self.surface = surface
        self.node = node
        self.cell = cell
        NN = mesh.number_of_nodes()

        self.localEdge = np.array([(1, 2), (2, 0), (0, 1)], **kwargs)
        self.localFace = np.array([(1, 2), (2, 0), (0, 1)], **kwargs)

        self.localLEdge = np.array([(1, 2), (2, 0), (0, 1)], **kwargs) #TODO
        self.localLFace = np.array([(1, 2), (2, 0), (0, 1)], **kwargs) #TODO

        if construct:
            self.construct()

        self.meshtype = 'ltri'

        self.nodedata = {}
        self.edgedata = {}
        self.celldata = {}
        self.meshdata = {}


    def construct():
        pass
    
    @classmethod
    def from_triangle_mesh(cls, mesh, p, surface=None):
        node = mesh.interpolation_points(p)
        cell = mesh.cell_to_ipoint(p)
        lmesh = cls(node, cell, p=p, construct=False)

        lmesh.face2cell = mesh.face_to_cell() # (NF, 4)
        lmesh.cell2face = mesh.cell_to_face()
        lmesh.face  = mesh.face_to_ipoint()
        return mesh 
 
    def vtk_cell_type(self, etype='cell'):
        """
        @berif  返回网格单元对应的 vtk类型。
        """
        if etype in {'cell', 2}:
            VTK_LAGRANGE_TRIANGLE = 69
            return VTK_LAGRANGE_TRIANGLE 
        elif etype in {'face', 'edge', 1}:
            VTK_LAGRANGE_CURVE = 68
            return VTK_LAGRANGE_CURVE

    def to_vtk(self, etype='cell', index=np.s_[:], fname=None):
        """
        Parameters
        ----------

        @berif 把网格转化为 VTK 的格式
        """
        from .vtk_extent import vtk_cell_index, write_to_vtu

        node = self.entity('node')
        GD = self.geo_dimension()
        if GD == 2:
            node = np.concatenate((node, np.zeros((node.shape[0], 1), dtype=self.ftype)), axis=1)

        #cell = self.entity(etype)[index]
        cell = self.entity(etype, index)
        cellType = self.vtk_cell_type(etype)
        idx = vtk_cell_index(self.p, cellType)
        NV = cell.shape[-1]

        cell = np.r_['1', np.zeros((len(cell), 1), dtype=cell.dtype), cell[:, idx]]
        cell[:, 0] = NV

        NC = len(cell)
        if fname is None:
            return node, cell.flatten(), cellType, NC 
        else:
            print("Writting to vtk...")
            write_to_vtu(fname, node, NC, cellType, cell.flatten(),
                    nodedata=self.nodedata,
                    celldata=self.celldata)