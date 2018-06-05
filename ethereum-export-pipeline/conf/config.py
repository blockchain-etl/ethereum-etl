def split_to_batches(start_incl, end_incl, batch_size):
    """start_incl and end_incl are inclusive, the returned batch ranges are also inclusive"""
    for batch_start in range(start_incl, end_incl + 1, batch_size):
        batch_end = min(batch_start + batch_size - 1, end_incl)
        yield batch_start, batch_end


# The first million blocks are in a single partition
# The next 3 million blocks are in 100k partitions
# The next 1 million blocks are in 10k partitions
# Note that there is a limit in Data Pipeline on the number of objects that can be increased in Support Center
# https://docs.aws.amazon.com/datapipeline/latest/DeveloperGuide/dp-limits.html
EXPORT_JOBS = [(0, 999999, 1000000)] + \
              [(start, end, 100000) for start, end in split_to_batches(1000000, 1999999, 1000000)] + \
              [(start, end, 100000) for start, end in split_to_batches(2000000, 2999999, 1000000)] + \
              [(start, end, 100000) for start, end in split_to_batches(3000000, 3999999, 1000000)] + \
              [(start, end, 10000) for start, end in split_to_batches(4000000, 4999999, 10000)]