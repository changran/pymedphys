# Copyright (C) 2019 Simon Biggs and Cancer Care Associates

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version (the "AGPL-3.0+").

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License and the additional terms for more
# details.

# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

# ADDITIONAL TERMS are also included as allowed by Section 7 of the GNU
# Affero General Public License. These additional terms are Sections 1, 5,
# 6, 7, 8, and 9 from the Apache License, Version 2.0 (the "Apache-2.0")
# where all references to the definition "License" are instead defined to
# mean the AGPL-3.0+.

# You should have received a copy of the Apache-2.0 along with this
# program. If not, see <http://www.apache.org/licenses/LICENSE-2.0>.


import os

import pydicom

from pymedphys_core.deliverydata.dicom import (
    dicom_to_delivery_data, delivery_data_to_dicom,
    get_gantry_angles_from_dicom, maintain_order_unique)

DATA_DIRECTORY = os.path.join(
    os.path.dirname(__file__), "data")
DICOM_FILEPATH = os.path.abspath(os.path.join(
    DATA_DIRECTORY, "RP.2.16.840.1.114337.1.1.1548043901.0_Anonymised.dcm"))


def num_of_control_points(dicom_dataset):
    return [
        len(beam.ControlPointSequence)
        for beam in dicom_dataset.BeamSequence
    ]


def source_to_surface_distances(dicom_dataset):
    SSDs = [
        {
            control_point.SourceToSurfaceDistance
            for control_point in beam_sequence.ControlPointSequence
        }
        for beam_sequence in dicom_dataset.BeamSequence
    ]

    return SSDs


# def reasign_meterset_weights(dicom_dataset):
#     for beam_sequence in dicom_dataset.BeamSequence:
#         for control_point in beam_sequence.ControlPointSequence:
#             control_point.CumulativeMetersetWeight = float(
#                 control_point.CumulativeMetersetWeight)


def first_mlc_positions(dicom_dataset):
    result = [
        beam_sequence.ControlPointSequence[0].BeamLimitingDevicePositionSequence[1].LeafJawPositions
        for beam_sequence in dicom_dataset.BeamSequence
    ]

    return result


def test_round_trip_dcm2dd2dcm():
    original = pydicom.dcmread(DICOM_FILEPATH, force=True)
    # reasign_meterset_weights(original)

    delivery_data = dicom_to_delivery_data(original)
    processed = delivery_data_to_dicom(
        delivery_data, original)
    # reasign_meterset_weights(processed)

    assert (
        num_of_control_points(original) == num_of_control_points(processed)
    )

    original_gantry_angles = get_gantry_angles_from_dicom(original)

    assert (
        maintain_order_unique(delivery_data.gantry) == original_gantry_angles)

    processed_gantry_angles = get_gantry_angles_from_dicom(processed)

    assert original_gantry_angles == processed_gantry_angles

    assert (
        source_to_surface_distances(original) ==
        source_to_surface_distances(processed))

    assert first_mlc_positions(original) == first_mlc_positions(processed)

    # TODO: Make delivery_data only be able to assign to already existing beams
    # Look for nearby gantry angles, assign all respective control_points to
    # that beam index
    assert str(original) == str(processed)
