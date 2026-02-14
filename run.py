#!/usr/bin/env python
"""Entry point para ejecutar la aplicación Yastubo"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.modules.module_a_identity.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
