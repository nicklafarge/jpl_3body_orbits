import requests
import json
import numpy as np


class System(object):

    def __init__(self, name, mass_ratio, radius_secondary, L1, L2, L3, L4, L5, lunit, tunit):
        self.name = name
        self.mass_ratio = float(mass_ratio)
        self.radius_secondary = float(radius_secondary)
        self.L1 = np.array(L1).astype('float')
        self.L2 = np.array(L2).astype('float')
        self.L3 = np.array(L3).astype('float')
        self.L4 = np.array(L4).astype('float')
        self.L5 = np.array(L5).astype('float')
        self.lunit = float(lunit)
        self.tunit = float(tunit)


class OrbitIC(object):

    def __init__(self, x, y, z, vx, vy, vz, jacobi, period, stability):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.vx = float(vx)
        self.vy = float(vy)
        self.vz = float(vz)

        self.jacobi = float(jacobi)
        self.period = float(period)
        self.stability = float(stability)

        self.state = np.array([self.x, self.y, self.z, self.vx, self.vy, self.vz])
        self.pos = np.array([self.x, self.y, self.z])
        self.vel = np.array([self.vx, self.vy, self.vz])

    def __repr__(self):
        np.set_printoptions(precision=3)
        return f"Orbit IC: {self.state}"

api_url = "https://ssd-api.jpl.nasa.gov/periodic_orbits.api"


def get_orbits(sys, family, libr=None, branch=None, periodmin=None, periodmax=None, periodunits=None,
              jacobimin=None, jacobimax=None, stabmin=None, stabmax=None):
    """

    :param sys: three-body system defined in lower-case as “primary-secondary,” e.g. earth-moon, mars-phobos, sun-earth.
    :param family: name of the orbit family:
                    halo, vertical, axial, lyapunov, longp, short, butterfly, dragonfly, resonant, dro, dpo, lpo.
    :param libr: libration point. Required for lyapunov,halo (1,2,3), longp, short (4,5),
                    and axial,vertical (1,2,3,4,5).
    :param branch: branch of orbits within the family: N/S for halo,dragonfly,butterfly, E/W for lpo,
                    and pq integer sequence for resonant (e.g., 12 for 1:2).
    :param periodmin: minimum period (inclusive). Units defined by periodunits.
    :param periodmax: maximum period (inclusive). Units defined by periodunits.
    :param periodunits: units of periodmin and periodmax: s for seconds, h for hours, d for days, TU for nondimensional.
    :param jacobimin: minimum Jacobi constant (inclusive). Nondimensional units.
    :param jacobimax: maximum Jacobi constant (inclusive). Nondimensional units.
    :param stabmin: minimum stability index (inclusive).
    :param stabmax: maximum stability index (inclusive).
    :return:
    """

    return request(sys=sys, family=family, libr=libr, branch=branch, periodmin=periodmin, periodmax=periodmax,
                   periodunits=periodunits, jacobimin=jacobimin, jacobimax=jacobimax, stabmin=stabmin, stabmax=stabmax)


def request(**kwargs):
    params = dict([(k, v) for k, v in kwargs.items() if v != None])
    response = requests.get(api_url, params=params)
    if response.status_code != 200:
        response.raise_for_status()

    orbit_data = json.loads(response.content)

    system = System(**orbit_data['system'])
    family = orbit_data['family']
    branch = orbit_data['branch']

    limits = orbit_data['limits']
    limits['jacobi'] = np.array(limits['jacobi']).astype('float')
    limits['period'] = np.array(limits['period']).astype('float')
    limits['stability'] = np.array(limits['stability']).astype('float')

    filter = orbit_data.pop('filter', None)
    count = orbit_data['count']
    fields = orbit_data['fields']
    orbit_ics = [OrbitIC(*x) for x in orbit_data['data']]

    return dict(system=system, family=family, branch=branch, limits=limits, filter=filter,
                count=count, fields=fields, orbit_ics=orbit_ics)


if __name__ == '__main__':
    family = get_orbits('earth-moon', 'halo', libr=2, branch='N', jacobimin=3.1, jacobimax=3.14)
