package it.unive.jlisa.witness.validator.model;

import java.util.Collections;
import java.util.List;

/**
 * The complete execution plan extracted from a violation witness.
 *
 * <p>The validator uses this plan to steer the target JVM towards the violation:
 * <ol>
 *   <li>{@link Interception}s — {@code Verifier.nondet*()} return values, injected via
 *       {@link com.sun.jdi.ThreadReference#forceEarlyReturn}</li>
 *   <li>{@link BranchDecision}s — branch directions, enforced via
 *       {@link com.sun.jdi.StackFrame#setValue} at breakpoints (v2 only)</li>
 *   <li>{@link AvoidPoint}s — locations whose execution signals a spurious witness</li>
 *   <li>{@link TargetPoint}s — locations whose execution confirms a correct witness</li>
 * </ol>
 */
public final class ViolationPlan {

	private final List<Interception> interceptions;
	private final List<BranchDecision> branchDecisions;
	private final List<AvoidPoint> avoidPoints;
	private final List<TargetPoint> targetPoints;

	public ViolationPlan(
			List<Interception> interceptions,
			List<BranchDecision> branchDecisions,
			List<AvoidPoint> avoidPoints,
			List<TargetPoint> targetPoints) {
		this.interceptions = Collections.unmodifiableList(interceptions);
		this.branchDecisions = Collections.unmodifiableList(branchDecisions);
		this.avoidPoints = Collections.unmodifiableList(avoidPoints);
		this.targetPoints = Collections.unmodifiableList(targetPoints);
	}

	public List<Interception> interceptions() {
		return interceptions;
	}

	public List<BranchDecision> branchDecisions() {
		return branchDecisions;
	}

	public List<AvoidPoint> avoidPoints() {
		return avoidPoints;
	}

	public List<TargetPoint> targetPoints() {
		return targetPoints;
	}

	public boolean isEmpty() {
		return interceptions.isEmpty() && branchDecisions.isEmpty()
				&& avoidPoints.isEmpty() && targetPoints.isEmpty();
	}

	@Override
	public String toString() {
		return "ViolationPlan{interceptions=" + interceptions.size()
				+ ", branches=" + branchDecisions.size()
				+ ", avoids=" + avoidPoints.size()
				+ ", targets=" + targetPoints.size() + "}";
	}
}
