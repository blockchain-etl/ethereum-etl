class StreamerAdapterStub:

    def open(self):
        pass

    def get_current_block_number(self):
        return 0

    def export_all(self, start_block, end_block, chain_id):
        pass

    def close(self):
        pass
