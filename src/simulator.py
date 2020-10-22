# -*- coding: utf-8 -*-
from random import randint, random as r

batch_size = 50
lot = 2000
fail_limit = 200

NOT_FOUND_PCT = 0.011
CONNECTION_FAIL_PCT = 0.002
VERIFICATION_FAIL_PCT = 0.025


def fc(batch, pct):
    """ Roll the dice to see how many should fail"""
    res = 0
    for i in range(batch):
        res += 1 if r() < pct else 0
    return res


def start_simulation():
    keep_going = True
    tick = 0
    ok = 0
    failed = 0
    remaining = lot
    # Handle these as queues
    conn_fail = []
    verify_fail = []
    deployed = []
    not_found = []
    print(f"Simulation using fail limit={fail_limit}, batch size={batch_size}")
    print(f"Running with {lot} CPEs to process")
    print()
    print("Iteration, deployed, not_found, connection_failed, "
          "verification_failed, failed, ok, failures %")
    while keep_going:
        tick += 1
        try:
            in_process = sum(deployed) + sum(not_found) + sum(conn_fail) + sum(
                verify_fail)
            if failed > fail_limit:
                print("Too many failed")
                keep_going = False
            elif in_process + failed < fail_limit and remaining > 0:
                # We can add more to the list
                batch = batch_size if remaining > batch_size else remaining
                deployed.insert(0, batch - randint(0, 2))
                remaining -= batch
            # Now, see if some of the CPEs can be moved along
            # TODO Need a better method to simulate continuous processing
            if deployed and (tick % 5 == 0 or len(deployed) > 3):
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

            fail_pct = failed * 100 / (failed + ok) if (failed + ok) else 0
            print((f"{tick}, {sum( deployed )}, "
                   f"{sum( not_found )}, "
                   f"{sum( conn_fail )}, "
                   f"{sum( verify_fail )}, "
                   f"{failed}, {ok}, "
                   f"{fail_pct:0.1f}%"))
            if remaining <= 0 and (not deployed and not not_found and not
                                   conn_fail and not verify_fail):
                print("Queue is empty. No remaining items to process.")
                keep_going = False

        except KeyboardInterrupt:
            keep_going = False


if __name__ == '__main__':
    print("Starting simulation")
    print("Each line represents status at 1 minute intervals.")

    start_simulation()
