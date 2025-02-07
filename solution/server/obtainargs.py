def extract_args(template_path, actual_path):
    template_parts = template_path.strip('/').split('/')
    actual_parts = actual_path.strip('/').split('/')
    
    if len(template_parts) != len(actual_parts):
        raise ValueError("Paths do not match in length")
    
    args = {}
    for template_part, actual_part in zip(template_parts, actual_parts):
        if template_part.startswith(':'):
            var_name = template_part[1:]
            args[var_name] = actual_part
        elif template_part != actual_part:
            raise ValueError("Paths do not match")
    
    return args

