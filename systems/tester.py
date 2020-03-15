def validate_state(state, testdata):
    print("validating game end state")
    goal = testdata["goal"]

    assert goal["hp"] == state.player.fighter.hp

    for idx, cd in enumerate(goal["cooldown"]):
        assert cd == state.player.caster.cooldowns[idx], state.player.caster.cooldowns

    assert len(goal["messages"]) == len(state.log.messages), len(state.log.messages)
    for idx, msg in enumerate(goal["messages"]):
        assert msg == state.log.messages[idx].text, state.log.messages[idx]
