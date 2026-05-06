def build_service_contract(summary):
    languages = summary["signals"]["languages"]
    has_frontend = summary["signals"]["has_frontend"]

    services = []

    if languages:
        sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)
        primary_lang = sorted_langs[0][0]

        services.append({
            "name": "backend",
            "language": primary_lang
        })

    if has_frontend:
        services.append({
            "name": "frontend",
            "language": "javascript"
        })

    return {
        "services": services
    }