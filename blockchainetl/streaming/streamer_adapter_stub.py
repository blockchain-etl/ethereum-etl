class StreamerAdapterStub:

    def open(self):
        pass

    def get_current_block_number(self):
        return 0

    def choose_block_base_on_delay_time(self, target_block, current_block):
        return self.get_current_block_number()

    def export_all(self, start_block, end_block):
        pass

    def close(self):
        pass
