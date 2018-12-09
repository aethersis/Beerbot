import unittest

from server_packet import ControllerPacket


class TestServerPacket(unittest.TestCase):
    def test_that_raises_for_out_of_bounds(self):
        packet = ControllerPacket()

        with self.assertRaises(ValueError):
            packet.camera_pitch = 1.01
        with self.assertRaises(ValueError):
            packet.camera_pitch = -1.01
        with self.assertRaises(ValueError):
            packet.camera_yaw = 1.01
        with self.assertRaises(ValueError):
            packet.camera_yaw = -1.01
        with self.assertRaises(ValueError):
            packet.robot_speed = 1.01
        with self.assertRaises(ValueError):
            packet.robot_speed = -1.01
        with self.assertRaises(ValueError):
            packet.robot_yaw = 1.01
        with self.assertRaises(ValueError):
            packet.robot_yaw = -1.01

    def test_that_works_for_values_within_bounds(self):
        packet = ControllerPacket()

        # If no exception is raised, the test passes
        packet.camera_pitch = 1
        packet.camera_pitch = -1
        packet.camera_yaw = 1
        packet.camera_yaw = -1
        packet.robot_speed = 1
        packet.robot_speed = -1
        packet.robot_yaw = 1
        packet.robot_yaw = -1

    def test_that_can_be_serialized_and_deserialized_properly(self):
        packet = ControllerPacket()
        packet.camera_yaw = 0.2
        packet.camera_pitch = 0.3
        packet.robot_yaw = -0.1
        packet.robot_speed = -0.5

        packets = list()
        serialized = packet.serialize()
        packet.deserialize(serialized)

        # both the constructor and deserialize method should give the same results and work correctly
        packets.append(packet)
        packets.append(ControllerPacket(serialized))

        for packet in packets:
            self.assertAlmostEqual(packet.camera_yaw, 0.2, 4)
            self.assertAlmostEqual(packet.camera_pitch, 0.3, 4)
            self.assertAlmostEqual(packet.robot_yaw, -0.1, 4)
            self.assertAlmostEqual(packet.robot_speed, -0.5, 4)
