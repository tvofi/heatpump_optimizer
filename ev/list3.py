muts += [
 ("U5-void-before-undo-point", "coordinator.py", "    entry, documents = coord.entry, await _async_store_documents(coord)\n", "    if scope != FACTORY_RESET_SCOPES[0]:\n        await coord.async_reset_heat_loss_learners()\n    entry, documents = coord.entry, await _async_store_documents(coord)\n"),
 ("U6-no-flush-before-documents", "coordinator.py", "    await _async_save_restored(coord)\n    return {name:", "    return {name:"),
]
