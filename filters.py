
# Return true to filter out the stats
def profit_filter(stats):
    return stats['profit'] <= 0

pre_filters = []
post_filters = [profit_filter]
