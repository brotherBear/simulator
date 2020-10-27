# -*- coding: utf-8 -*-
from random import randint, random as r

NOT_FOUND_PCT = 0.011
CONNECTION_FAIL_PCT = 0.002
VERIFICATION_FAIL_PCT = 0.023


def fc(batch, pct):
    """ Roll the dice to see how many should fail"""
    res = 0
    for i in range(batch):
        res += 1 if r() < pct else 0
    return res


def start_simulation(lot, batch, limit):
    """
    Perform a simulation.
    """
    keep_going = True
    tick = 0
    ok = 0
    failed = 0
    remaining = lot
    message = None
    # Handle these as queues
    conn_fail = []
    verify_fail = []
    deployed = []
    not_found = []
    while keep_going:
        tick += 1
        try:
            in_process = sum(deployed) + sum(not_found) + sum(conn_fail) + sum(
                verify_fail)
            if in_process + failed < limit and remaining > 0:
                # We can add more to the list
                batch = batch if remaining > batch else remaining
                deployed.insert(0, batch - randint(0, 2))
                remaining -= batch
            # Now, see if some of the CPEs can be moved along
            if (deployed and tick > 5) or len(deployed) == 5:
                # Every 5 minutes we see if the "deployed" can be moved along.
                verify_batch = deployed.pop()
                nf = fc(verify_batch, NOT_FOUND_PCT)
                cf = fc(verify_batch - nf, CONNECTION_FAIL_PCT)
                vf = fc(verify_batch - nf - cf, VERIFICATION_FAIL_PCT)
                ok += verify_batch - nf - cf - vf
                not_found.insert(0, nf)
                conn_fail.insert(0, cf)
                verify_fail.insert(0, vf)
            if tick % 2 == 0:
                failed += not_found.pop() if not_found else 0
                failed += conn_fail.pop() if conn_fail else 0
                failed += verify_fail.pop() if verify_fail else 0

            if remaining <= 0 and (not deployed and not not_found and not
                                   conn_fail and not verify_fail):
                message = "Queue is empty. No remaining items to process."
                keep_going = False
            if failed >= limit:
                message = "Too many failed. Stop the process!"
                keep_going = False

        except KeyboardInterrupt:
            keep_going = False

    fail_pct = failed * 100 / (failed + ok) if (failed + ok) else 0
    return ((f"{lot}, {limit}, {batch}, "
             f"{tick}, {sum( deployed )}, "
             f"{sum( not_found )}, "
             f"{sum( conn_fail )}, "
             f"{sum( verify_fail )}, "
             f"{failed}, {ok}, "
             f"{fail_pct:0.1f}%, {message}"))


if __name__ == '__main__':
    print("Starting simulation")
    print("Each line represents status end of simulation.")

    print("Max_upgrades, max_failures, batch_size, "
          "Iteration, deployed, not_found, connection_failed, "
          "verification_failed, failed, ok, failures %, message")
    for lot in [1000, 2000, 5000]:
        for limit in [50, 100, 200]:
            for batch in range(10, limit * 2 + 1, 10):
                print(start_simulation(lot, batch, limit))
