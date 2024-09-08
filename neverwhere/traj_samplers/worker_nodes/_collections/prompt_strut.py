def verify_prompt(prompt_dict):
    assert "foreground_prompt" in prompt_dict, "foreground_prompt not found in prompt_dict"
    assert "background_prompt" in prompt_dict, "background_prompt not found in prompt_dict"
    assert "negative_prompt" in prompt_dict, "negative_prompt not found in prompt_dict"
    assert "cone_prompt" in prompt_dict, "cone_prompt not found in prompt_dict"