from typing import Self


class BoundingBox2D:
    """
    A simple 2D axis-aligned bounding box, defined by its min/max coordinates:
    (min_x, min_y) is the bottom-left corner,
    (max_x, max_y) is the top-right corner.

    Attributes:
        min_x (float): Minimum x-coordinate
        min_y (float): Minimum y-coordinate
        max_x (float): Maximum x-coordinate
        max_y (float): Maximum y-coordinate
    """

    def __init__(self, min_x: float, min_y: float, max_x: float, max_y: float):
        """
        Args:
            min_x (float): Minimum x-coordinate.
            min_y (float): Minimum y-coordinate.
            max_x (float): Maximum x-coordinate.
            max_y (float): Maximum y-coordinate.

        Raises:
            ValueError: If min values are greater than max values.
        """
        if min_x > max_x or min_y > max_y:
            raise ValueError("Minimum coordinates must be less than or equal"
                             "to the maximum coordinates.")

        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y

    @property
    def width(self) -> float:
        return self.max_x - self.min_x

    @property
    def height(self) -> float:
        return self.max_y - self.min_y

    @property
    def area(self) -> float:
        return self.width * self.height

    def contains_point(self, x: float, y: float) -> bool:
        return (self.min_x <= x <= self.max_x and
                self.min_y <= y <= self.max_y)

    def intersects(self, other: Self) -> bool:
        """
        Check if this bounding box intersects with another.

        Args:
            other: BoundingBox2D - another bounding box.

        Returns:
            bool: True if the boxes overlap, else False.
        """
        return not (
            self.max_x < other.min_x or
            self.min_x > other.max_x or
            self.max_y < other.min_y or
            self.min_y > other.max_y
        )

    def intersection(self, other: Self) -> "BoundingBox2D | None":
        """
        Compute the intersection of this box with another.

        Args:
            other: BoundingBox2D - another bounding box.

        Returns:
            BoundingBox2D or None: The overlapping region, or None if no overlap.
        """
        if not self.intersects(other):
            return None

        return BoundingBox2D(
            max(self.min_x, other.min_x),
            max(self.min_y, other.min_y),
            min(self.max_x, other.max_x),
            min(self.max_y, other.max_y),
        )

    def union(self, other: Self) -> "BoundingBox2D":
        """
        Compute the smallest bounding box that contains both boxes.

        Args:
            other (BoundingBox2D): Another bounding box.

        Returns:
            BoundingBox2D: The union bounding box.
        """
        return BoundingBox2D(
            min(self.min_x, other.min_x),
            min(self.min_y, other.min_y),
            max(self.max_x, other.max_x),
            max(self.max_y, other.max_y),
        )

    def __repr__(self) -> str:
        """Return a string representation of the bounding box."""
        return (f"BoundingBox2D(min_x={self.min_x}, min_y={self.min_y}, "
                f"max_x={self.max_x}, max_y={self.max_y})")
