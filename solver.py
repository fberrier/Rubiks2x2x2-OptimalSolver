# ###################### The solve function computes all optimal solving maneuvers #####################################
import rubiks.thirdparties.hkociemba.face as face
import rubiks.thirdparties.hkociemba.cubie as cubie
import rubiks.thirdparties.hkociemba.coord as coord
import rubiks.thirdparties.hkociemba.enums as en
import rubiks.thirdparties.hkociemba.moves as mv
import rubiks.thirdparties.hkociemba.pruning as pr
from rubiks.thirdparties.hkociemba.defs import N_TWIST

solutions = []


def search(cornperm, corntwist, sofar, togo):
    global solutions
    # ##############################################################################################################
    if togo == 0:
        if len(solutions) == 0 or (len(solutions[-1]) == len(sofar)):
            solutions.append(sofar[:])
    else:
        for m in en.Move:

            if len(sofar) > 0:
                if sofar[-1] // 3 == m // 3: # successive moves on same face
                    continue

            cornperm_new = mv.cornperm_move[9 * cornperm + m]
            corntwist_new = mv.corntwist_move[9 * corntwist + m]

            if pr.corner_depth[N_TWIST * cornperm_new + corntwist_new] >= togo:
                continue  # impossible to reach solved cube in togo - 1 moves

            sofar.append(m)
            search(cornperm_new, corntwist_new, sofar, togo - 1)
            sofar.pop(-1)


def solve(cubestring):
    """Solves a 2x2x2 cube defined by its cube definition string.
     :param cubestring: The format of the string is given in the Facelet class defined in the file enums.py
     :return A list of all optimal solving maneuvers
    """
    global solutions
    fc = face.FaceCube()
    s = fc.from_string(cubestring) #####################################################################################
    if s is not True:
        raise ValueError(s)  # Error in facelet cube
    cc = fc.to_cubie_cube()
    s = cc.verify()
    if s != cubie.CUBE_OK:
        raise ValueError(s)  # Error in cubie cube

    solutions = []
    co_cube = coord.CoordCube(cc)

    togo = pr.corner_depth[N_TWIST * co_cube.cornperm + co_cube.corntwist]
    search(co_cube.cornperm, co_cube.corntwist, [], togo)

    s = ''
    for i in range(min(len(solutions), 1)):  # use  range(min(len(solutions), 1)) if you want to return only a single solution
        ps = ''
        for m in solutions[i]:
            ps += m.name + ' '
        #ps += '(' + str(len(ps)//3) + 'f)\r\n'
        s += ps
    return s
########################################################################################################################

