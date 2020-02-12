using System;
using System.Collections.Generic;
using System.Text;

namespace ifttt
{
    /// <summary>
    /// Wrapper around a dictionary to help count the number of
    /// times a particular element has been seen.
    /// </summary>
    /// <typeparam name="T">Type of elements to count.</typeparam>
    public class Counter<T> : Dictionary<T, int>
    {
        public Counter()
            : base()
        {
        }
        public Counter(IEqualityComparer<T> eq)
            : base(eq)
        {
        }
        /// <summary>
        /// Increase the count of the specified element by one.
        /// </summary>
        /// <param name="t">Element whose count is to be incremented.</param>
        /// <returns>The number of times the element has been seen, including this call.</returns>
        public int Increment(T t)
        {
            return Increment(t, 1);
        }

        /// <summary>
        /// Increase the count of the specified element by the specified amount.
        /// </summary>
        /// <param name="t">Element whose count is to be incremented.</param>
        /// <param name="iCount">Number of counts to add.  Must be positive.</param>
        /// <returns>The updaetd count of the specified element.</returns>
        /// <exception cref="System.Exception">thrown if count is zero or negative</exception>
        public int Increment(T t, int iCount)
        {
            if (iCount <= 0)
            {
                throw new Exception("Increment amount must be positive!");
            }
            int iCurVal;
            if (!TryGetValue(t, out iCurVal))
            {
                iCurVal = 0;
            }
            iCurVal += iCount;
            this[t] = iCurVal;
            return iCurVal;
        }

        /// <summary>
        /// Decrease the count of the specified element by one.  If no counts are
        /// remaining, the key value pair is removed from the dictionary.
        /// </summary>
        /// <param name="t">Element whose count is to be decremented.</param>
        /// <returns>The updated element count after decrement.</returns>
        /// <exception cref="System.Exception">thrown if the element already has 0 count.</exception>
        public int Decrement(T t)
        {
            int iCurVal;
            if (!TryGetValue(t, out iCurVal))
            {
                throw new Exception("Tried to decrement 0-count element!");
            }
            if (iCurVal <= 0)
            {
                throw new Exception("Counter contains non-positive value!");
            }
            --iCurVal;
            if (0 == iCurVal)
            {
                Remove(t);
            }
            else
            {
                this[t] = iCurVal;
            }
            return iCurVal;
        }

        public int GetCount(T t)
        {
            int iCurVal;
            if (!TryGetValue(t, out iCurVal))
                return 0;
            return iCurVal;
        }

        /// <summary>
        /// Given another counter, update this counter to be:
        /// this[t] = max(this[t], c[t]) for all t.
        /// That is, set the counter to hold the maximum of
        /// all counts from this counter or the specified one.
        /// </summary>
        /// <param name="c">Other counter to be comined.</param>
        public void CombineMax(Counter<T> c)
        {
            foreach (KeyValuePair<T, int> p in c)
            {
                int iCurVal = 0;
                if (!TryGetValue(p.Key, out iCurVal) || iCurVal < p.Value)
                    this[p.Key] = p.Value;
            }
        }
    }
}
