"""
World validation logic for the Robot Universe MUD.

Can be imported and called directly (for tests) or run as a management command
via ``evennia validate_world``.
"""


def validate_world():
    """
    Run all world validation checks.

    Returns:
        list[str]: A list of error strings. An empty list means the world is valid.
    """
    errors = []
    errors.extend(check_exit_validity())
    errors.extend(check_room_connectivity())
    errors.extend(check_npc_home_locations())
    errors.extend(check_mission_integrity())
    errors.extend(check_repairable_objects())
    return errors


def check_exit_validity():
    """
    Check that every exit's destination exists.

    Returns:
        list[str]: Error strings for exits with missing or None destinations.
    """
    import evennia

    errors = []
    exits = evennia.search_object(typeclass="evennia.objects.objects.DefaultExit")
    for exit_obj in exits:
        if exit_obj.destination is None:
            location_name = exit_obj.location.key if exit_obj.location else "<no location>"
            errors.append(
                f"Exit '{exit_obj.key}' in '{location_name}' has no valid destination"
            )
        else:
            # Verify the destination object actually exists in the database
            try:
                dest = exit_obj.destination
                # Accessing .pk will raise if the object is a stale reference
                _ = dest.pk
            except Exception:
                location_name = exit_obj.location.key if exit_obj.location else "<no location>"
                errors.append(
                    f"Exit '{exit_obj.key}' in '{location_name}' has no valid destination"
                )
    return errors


def check_room_connectivity():
    """
    Perform a BFS from the first room and verify every room is reachable.

    Returns:
        list[str]: Error strings for rooms not reachable from the starting room.
    """
    import evennia

    errors = []
    rooms = list(evennia.search_object(typeclass="typeclasses.rooms.StationRoom"))
    if not rooms:
        return errors  # No rooms to check

    start = rooms[0]
    visited = set()
    queue = [start]

    while queue:
        current = queue.pop(0)
        if current.pk in visited:
            continue
        visited.add(current.pk)
        for exit_obj in current.exits:
            dest = exit_obj.destination
            if dest is not None and dest.pk not in visited:
                queue.append(dest)

    for room in rooms:
        if room.pk not in visited:
            errors.append(
                f"Room '{room.key}' is not reachable from '{start.key}'"
            )

    return errors


def check_npc_home_locations():
    """
    Check that every NPC's ``db.home_location`` references a valid room object.

    Returns:
        list[str]: Error strings for NPCs with invalid home locations.
    """
    import evennia

    errors = []
    npcs = evennia.search_object(typeclass="typeclasses.objects.NPC")
    for npc in npcs:
        home = npc.db.home_location
        if home is None:
            errors.append(f"NPC '{npc.key}' has invalid home_location")
        else:
            try:
                _ = home.pk
            except Exception:
                errors.append(f"NPC '{npc.key}' has invalid home_location")
    return errors


def check_mission_integrity():
    """
    Verify mission data integrity:

    - The ``giver_npc`` name resolves to an existing NPC in the world.
    - Each objective target matches an existing entity:
      - destroy objectives: target matches a Hostile name
      - collect objectives: target matches an Artifact name
      - visit objectives: target matches a StationRoom name
      - deliver objectives: target matches an Artifact name and destination matches a room

    Returns:
        list[str]: Error strings for missions with broken references.
    """
    import evennia

    errors = []

    try:
        from world.missions import MISSIONS
    except ImportError:
        errors.append("Could not import MISSIONS from world.missions")
        return errors

    for mission_id, mission in MISSIONS.items():
        # Check giver NPC exists
        giver_name = mission.get("giver_npc", "")
        if giver_name:
            matches = evennia.search_object(
                giver_name, typeclass="typeclasses.objects.NPC"
            )
            if not matches:
                errors.append(
                    f"Mission '{mission_id}': giver NPC '{giver_name}' not found"
                )

        # Check objective targets exist
        for objective in mission.get("objectives", []):
            obj_type = objective.get("type", "")
            target_name = objective.get("target", "")

            if obj_type == "destroy":
                if target_name:
                    matches = evennia.search_object(
                        target_name, typeclass="typeclasses.objects.Hostile"
                    )
                    if not matches:
                        errors.append(
                            f"Mission '{mission_id}': destroy target '{target_name}' not found"
                        )

            elif obj_type == "collect":
                if target_name:
                    matches = evennia.search_object(
                        target_name, typeclass="typeclasses.objects.Artifact"
                    )
                    # Also check Equipment (subclass of Artifact)
                    if not matches:
                        matches = evennia.search_object(
                            target_name, typeclass="typeclasses.objects.Equipment"
                        )
                    if not matches:
                        errors.append(
                            f"Mission '{mission_id}': collect target '{target_name}' not found"
                        )

            elif obj_type == "visit":
                if target_name:
                    matches = evennia.search_object(
                        target_name, typeclass="typeclasses.rooms.StationRoom"
                    )
                    if not matches:
                        errors.append(
                            f"Mission '{mission_id}': visit target '{target_name}' not found"
                        )

            elif obj_type == "deliver":
                if target_name:
                    matches = evennia.search_object(
                        target_name, typeclass="typeclasses.objects.Artifact"
                    )
                    if not matches:
                        matches = evennia.search_object(
                            target_name, typeclass="typeclasses.objects.Equipment"
                        )
                    if not matches:
                        errors.append(
                            f"Mission '{mission_id}': deliver target '{target_name}' not found"
                        )
                destination = objective.get("destination", "")
                if destination:
                    matches = evennia.search_object(
                        destination, typeclass="typeclasses.rooms.StationRoom"
                    )
                    if not matches:
                        errors.append(
                            f"Mission '{mission_id}': deliver destination '{destination}' not found"
                        )

        # Check reward items exist
        for item_key in mission.get("reward_items", []):
            if item_key:
                matches = evennia.search_object(item_key)
                if not matches:
                    errors.append(
                        f"Mission '{mission_id}': reward item '{item_key}' not found"
                    )

    return errors


def check_repairable_objects():
    """
    Verify that every RepairableObject's required artifacts exist in the world.

    Returns:
        list[str]: Error strings for repairable objects with missing artifact requirements.
    """
    import evennia

    errors = []
    repairable_objects = evennia.search_object(
        typeclass="typeclasses.objects.RepairableObject"
    )
    for obj in repairable_objects:
        cost = obj.db.repair_cost or {}
        for item_name, qty in cost.items():
            matches = evennia.search_object(item_name)
            if not matches:
                errors.append(
                    f"RepairableObject '{obj.key}': required artifact '{item_name}' not found in world"
                )
    return errors
