package mn.edu.must.sqat;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class BonusTest {
    @Test
    @DisplayName("B1 all-defs: score 49->54->56; present 35/40->40/50; best 37/43->42/53")
    void bonus_belowThresholdLongStreak_returnsThree() {
        assertEquals(3, DataFlowTargets.bonus(new int[]{1,1,1,1,1}, 6));
    }

    @Test
    @DisplayName("B2 all-defs: score 51->54->56; streak 36/41/46->41,41->42/43")
    void bonus_atThresholdInterruptedLongStreak_returnsEight() {
        assertEquals(8, DataFlowTargets.bonus(new int[]{1,1,1,1,1,0,1}, 6));
    }

    @Test
    @DisplayName("B3 DU: attendance 31->38 F; present 35->50; best 37->53 F; score 51->56")
    void bonus_emptyZeroThreshold_returnsFive() {
        assertEquals(5, DataFlowTargets.bonus(new int[]{}, 0));
    }

    @Test
    @DisplayName("B4 DU: score 49->56; present 35->50 F; best 37->53 F")
    void bonus_emptyPositiveThreshold_returnsZero() {
        assertEquals(0, DataFlowTargets.bonus(new int[]{}, 1));
    }

    @Test
    @DisplayName("B5 DU: a 38->39 F; streak 46 kills 36/41; best 37->53")
    void bonus_allAbsent_returnsZero() {
        assertEquals(0, DataFlowTargets.bonus(new int[]{0,-1,0}, 1));
    }

    @Test
    @DisplayName("B6 DU: streak 46->41; best 37->42 T; score 51->56")
    void bonus_initialAbsenceThenPresent_returnsFive() {
        assertEquals(5, DataFlowTargets.bonus(new int[]{0,1}, 1));
    }

    @Test
    @DisplayName("B7 DU: best 43->42 F/T,43->53 F; streak 41->41; score 51->56")
    void bonus_splitFivePresent_returnsFive() {
        assertEquals(5, DataFlowTargets.bonus(new int[]{1,1,0,1,1,1}, 5));
    }

    @Test
    @DisplayName("B8 DU: attendance 31->32 T short circuit")
    void bonus_nullAttendance_throws() {
        assertThrows(IllegalArgumentException.class, () -> DataFlowTargets.bonus(null, 0));
    }

    @Test
    @DisplayName("B9 DU: threshold 31->32 T after attendance nonnull")
    void bonus_negativeThreshold_throws() {
        assertThrows(IllegalArgumentException.class, () -> DataFlowTargets.bonus(new int[]{}, -1));
    }

    @Test
    @DisplayName("B10 boundary: best 43->53 T after more than five consecutive days")
    void bonus_sixConsecutive_returnsEight() {
        assertEquals(8, DataFlowTargets.bonus(new int[]{1,1,1,1,1,1}, 6));
    }
}
